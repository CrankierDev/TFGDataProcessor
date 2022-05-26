import os

import db
import sqlite3
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

from tkinter import ttk
from tkinter import *
from model import AeroData
from ReadProperties import Properties
from graphsModule import *


class DataProcess:

    def __init__(self, root):
        '''Defining global parameters'''
        # Properties file
        self.dbArchiveRoots = None
        self.properties = Properties('resources/configuration.properties').getProperties()
        # Get archives root from properties
        self.archivesRoot = self.properties['archivesRoot']  # List of directories to get new data

        self.window = root
        self.window.title("Processing data application")  # Title
        self.window.resizable(0, 0)  # Resizing active. Each value is an axis, set (1,1) to active both.
        self.window.iconphoto(True, tk.PhotoImage(file='resources/dataIcon.png'))  # Sets an icon to the app.

        frame = LabelFrame(self.window, text="Processes", font=('Calibri', 16, 'bold'))
        frame.grid(row=0, rowspan=1, columnspan=6, pady=1)

        # Button set to execute methods
        buttonStyle = ttk.Style()
        buttonStyle.configure('TButton', font=('Calibri', 14, 'bold'))
        # Button to read new files
        self.updateLogsButton = ttk.Button(frame, text="Update data",
                                           command=self.addNewData, style="TButton")
        self.updateLogsButton.grid(row=1, column=1, columnspan=1, sticky=W)

        # Button to graph new data
        self.graphDataButton = ttk.Button(frame, text="Graph data",
                                          command=self.graphData, style="TButton")
        self.graphDataButton.grid(row=1, column=5, columnspan=1, sticky=W)

        # Informative message
        self.message = Label(text='', fg='red')
        self.message.grid(row=4, column=0, columnspan=2, sticky=W + E)

        # Table of logs in database
        # Personalize table style
        style = ttk.Style()
        # General settings of ext
        style.configure('Treeview', highlightthickness=0, bd=0, font=('Calibri', 11))
        # Modifying heading
        style.configure('Treeview.Heading', font=('Calibri', 14, 'bold'))
        # Set it borderless.
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        # Define table structure
        self.table = ttk.Treeview(height=30, columns=("#1", "#2", "#3", "#4", "#5", "#6"), style="Treeview")
        # At last line, we only need to add new #, #0 comes by default
        # Set a unique width for columns
        self.columnWidth = 140
        self.table.grid(row=5, column=0, columnspan=2)
        self.table.heading('#0', text='Method', anchor=CENTER)
        self.table.heading('#1', text='Simulation', anchor=CENTER)
        self.table.heading('#2', text='AOA', anchor=CENTER)
        self.table.heading('#3', text='Y+', anchor=CENTER)
        self.table.heading('#4', text='Cd', anchor=CENTER)
        self.table.heading('#5', text='Cl', anchor=CENTER)
        self.table.heading('#6', text='Efficiency', anchor=CENTER)
        self.table.column('#0', anchor=CENTER, width=self.columnWidth)
        self.table.column('#1', anchor=CENTER, width=self.columnWidth)
        self.table.column('#2', anchor=CENTER, width=self.columnWidth)
        self.table.column('#3', anchor=CENTER, width=self.columnWidth)
        self.table.column('#4', anchor=CENTER, width=self.columnWidth)
        self.table.column('#5', anchor=CENTER, width=self.columnWidth)
        self.table.column('#6', anchor=CENTER, width=self.columnWidth)

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(orient="vertical", command=self.table.yview)
        self.scrollbar.grid(row=5, column=3, sticky='nse')
        self.table.configure(yscrollcommand=self.scrollbar.set)

        self.getLogs()

    # This method refreshes table data
    def getLogs(self):
        # First, clean the table to not duplicate data
        tableLogs = self.table.get_children()

        for row in tableLogs:
            self.table.delete(row)

        # Get data from database
        dataLogging = db.session.query(AeroData).order_by(AeroData.id.desc()).all()

        # Plot data at the table
        for row in dataLogging:
            self.table.insert('', 0, text=row.method,
                              values=(row.simulation, row.angleOfAttack, row.yPlus,
                                      row.dragCoeff, row.liftCoeff, row.efficiency))

        # Refresh list of roots
        dbArchivesRoots = db.session.query(AeroData.urlData).all()
        self.dbArchiveRoots = []
        for archive in dbArchivesRoots:
            self.dbArchiveRoots.append(archive.urlData)

        # print('roots=', self.dbArchiveRoots)

    # Method to catch new logs
    def addNewData(self):
        # Variable for new data
        newLogsList = []

        # Loops to navigate inside roots
        for roots in self.archivesRoot:
            path = self.archivesRoot[roots]
            folders = os.listdir(path)

            for folder in folders:
                folderPath = path + folder + '/'
                simulations = os.listdir(folderPath)

                for simulation in simulations:
                    simulationFolder = folderPath + simulation + '/'

                    if simulationFolder not in self.dbArchiveRoots:
                        logRoute = simulationFolder + 'log'

                        try:

                            # Openning log file and processing data
                            with open(logRoute, "r") as file:
                                info = file.readlines()
                                index = -15
                                infoInit = info[index]

                                while not infoInit.startswith("forceCoeffs"):
                                    index += 1
                                    infoInit = info[index]

                                    if index == 0:
                                        break

                                coeffs = []
                                index += 2

                                for i in range(2):
                                    coeffsFeed = info[index + i].split('=')[1].strip('\n')
                                    coeffs.append(float(coeffsFeed))

                                # Lets control if YPlus has been writed
                                readYPlus = True
                                while not infoInit.startswith("yPlus"):
                                    index += 1
                                    infoInit = info[index]

                                    if infoInit.startswith("End"):
                                        readYPlus = False
                                        break

                                if readYPlus:
                                    index += 2
                                    yPlusFeed = info[index].split('=')[3].strip()
                                    coeffs.append(float(yPlusFeed))

                                    newLog = AeroData(roots, folder, simulation, simulationFolder,
                                                      round(coeffs[0], 3), round(coeffs[1], 3),
                                                      round(coeffs[2], 3))
                                else:
                                    newLog = AeroData(roots, folder, simulation, simulationFolder,
                                                      round(coeffs[0], 3), round(coeffs[1], 3), None)

                            newLogsList.append(newLog)

                        except FileNotFoundError:
                            print(f"There is no log file on {simulationFolder}.")

                        except ValueError:
                            print(f"Log file on {simulationFolder} has format errors.")

        if newLogsList:
            for log in newLogsList:
                db.session.add(log)

            db.session.commit()

            print(f"{len(newLogsList)} new entries generated in the database.")
        else:
            print("No new entries were added to the database.")

        self.getLogs()

    # Define a method which make graphs and save it at folders
    def graphData(self):
        # Set a list with all simulations
        ''' dbSimulations = db.session.query(AeroData).all()
        simulations = []
        for dbSimulation in dbSimulations:
            if dbSimulation.simulation not in simulations:
                simulations.append(dbSimulation.simulation)'''

        # Each simulation must be collected in a bigger dictionary
        plotsData = {}  # Dictionary with all data from new plots
        simulationData = {}  # Dictionary with data of each new simulation
        for method in self.archivesRoot:
            dbSimulations = db.session.query(AeroData).filter_by(method=method).all()
            simulations = []

            for dbSimulation in dbSimulations:
                if dbSimulation.simulation not in simulations:
                    simulations.append(dbSimulation.simulation)
            # simulations = db.session.query(AeroData).filter_by(method=method).all()

            dirFiles = os.listdir()
            if method + ' drag coefficient.png' not in dirFiles or \
                    method + ' lift coefficient.png' not in dirFiles or \
                    method + ' efficiency.png' not in dirFiles or \
                    method + ' polar.png' not in dirFiles:

                simulationData = {}
                for simulation in simulations:
                    # Collect data of the simulation from DB
                    dbDataFromSimulation = db.session.query(AeroData).filter_by(method=method).filter_by(simulation=simulation).all()

                    # Preprocess dataset from query with a dictionary
                    processedData = {'alpha': [],
                                     'cl': [],
                                     'cd': [],
                                     'ef': []}

                    for data in dbDataFromSimulation:
                        processedData['alpha'].append(int(data.angleOfAttack.replace(' degrees', '')))

                    processedData['alpha'].sort()
                    for alpha in processedData['alpha']:
                        for i, data in enumerate(dbDataFromSimulation):
                            if data.angleOfAttack == str(alpha) + ' degrees':
                                processedData['cl'].append(data.liftCoeff)
                                processedData['cd'].append(data.dragCoeff)
                                processedData['ef'].append(data.efficiency)

                                dbDataFromSimulation.pop(i)

                    simulationData[simulation] = processedData

                plotsData[method] = simulationData

        if plotsData != {}:
            # Graph data from properties
            colorList = self.properties['colorList'].split(',')  # Color list for graphs
            fontSize = self.properties['fontSize']
            labelsFontSize = self.properties['labelsFontSize']

        # Plot data with matplotlib
        # Relevant parameters for plots axis
        graphSettings = {}
        for key in plotsData.keys():
            alpha_min, alpha_max, cl_min, cl_max, cd_min, cd_max, ef_min, yef_max = 1, 0, 1, 0, 1, 0, 1, 0
            for simulation in plotsData[key]:
                aux_alpha_min = min(plotsData[key][simulation]['alpha'])
                if aux_alpha_min < alpha_min:
                    alpha_min = aux_alpha_min

                aux_alpha_max = max(plotsData[key][simulation]['alpha'])
                if aux_alpha_max > alpha_max:
                    alpha_max = aux_alpha_max

                aux_cl_min = min(plotsData[key][simulation]['cl'])
                if aux_cl_min < cl_min:
                    cl_min = aux_cl_min

                aux_cl_max = max(plotsData[key][simulation]['cl'])
                if aux_cl_max > cl_max:
                    cl_max = aux_cl_max

                aux_cd_min = min(plotsData[key][simulation]['cd'])
                if aux_cd_min < cd_min:
                    cd_min = aux_cd_min

                aux_cd_max = max(plotsData[key][simulation]['cd'])
                if aux_cd_max > cd_max:
                    cd_max = aux_cd_max

                aux_ef_min = min(plotsData[key][simulation]['ef'])
                if aux_ef_min < ef_min:
                    ef_min = aux_ef_min

                aux_ef_max = max(plotsData[key][simulation]['ef'])
                if aux_ef_max > yef_max:
                    yef_max = aux_ef_max

            graphSettings[key] = {
                'alpha_min': round(alpha_min - 2, 0),
                'alpha_max': round(alpha_max + 2, 0),
                'cl_min': round(cl_min - 0.2, 1),
                'cl_max': round(cl_max + 0.2, 1),
                'cd_min': round(cd_min, 1),
                'cd_max': round(cd_max + 0.05, 1),
                'ef_min': round(ef_min - 2, 0),
                'ef_max': round(yef_max + 2, 0)
            }

        for key in plotsData.keys():
            if key == 'method1':
                key = '10%c suction slot active'
            elif key == 'method2':
                key = '70%c suction slot active'
            elif key == 'method3':
                key = 'Both suction slots active'
            elif key == 'method4':
                key = '10%c suction slot passive, 70%c active'
            elif key == 'method5':
                key = '10%c suction slot active, 70%c passive'

            # Lift plot
            plot_name = key + ' lift coefficient'
            grapher(plot_name, 'alpha', 'cl', plotsData, key, graphSettings, colorList, fontSize, labelsFontSize)

            # Drag plot
            plot_name = key + ' drag coefficient'
            grapher(plot_name, 'alpha', 'cd', plotsData, key, graphSettings, colorList, fontSize, labelsFontSize)

            # Polar plot
            plot_name = key + ' polar'
            grapher(plot_name, 'cd', 'cl', plotsData, key, graphSettings, colorList, fontSize, labelsFontSize)

            # Efficiency plot
            plot_name = key + ' efficiency'
            grapher(plot_name, 'alpha', 'ef', plotsData, key, graphSettings, colorList, fontSize, labelsFontSize)


if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)  # Creates the data model
    root = tk.Tk()  # Main window
    app = DataProcess(root)  # Gives DataProcess class the window control.
    root.mainloop()
