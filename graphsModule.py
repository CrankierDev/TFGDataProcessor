import matplotlib.pyplot as plt
import numpy as np

def title_selector(data):
    if data == 'alpha':
        title = r'$\alpha$'
    elif data == 'cd':
        title = r'$c_d$'
    elif data == 'cl':
        title = r'$c_l$'
    elif data == 'ef':
        title = 'Efficiency'

    return title

def arranger_selector(data):
    if data == 'cl':
        arranger = 0.25
    elif data == 'cd':
        arranger = 0.05
    elif data == 'ef':
        arranger = 5
    elif data == 'alpha':
        arranger = 2

    return arranger

def grapher(title, data_x, data_y, plotsData, key, graphSettings, colorList, fontSize, labelsFontSize):
    # Axis data
    y_min = data_y + '_min'
    y_max = data_y + '_max'
    x_min = data_x + '_min'
    x_max = data_x + '_max'
    x_title = title_selector(data_x)
    y_title = title_selector(data_y)
    x_arranger = arranger_selector(data_x)
    y_arranger = arranger_selector(data_y)
    savingName = title + '.png'

    plt.figure(title, figsize=(12.5, 10))

    for i, simulation in enumerate(plotsData[key]):
        # print(simulation.replace('flap_', '').replace('_def', ''))
        sim_name = simulation
        linestyle = 'solid'
        simulationLegend = sim_name
        legendLocation = 'lower right'

        if 'flap' in sim_name:
            sim_name = simulation.replace('flap_', '').replace('_def', '')

            if int(sim_name) < 0:
                linestyle = 'dashed'
            else:
                linestyle = 'solid'

            simulationLegend = simulation.replace('flap_', 'flap deflected ').replace('_def', ' degrees')

        plt.plot(plotsData[key][simulation][data_x], plotsData[key][simulation][data_y],
                 linestyle=linestyle, marker='o', label=simulationLegend, color=colorList[i - 1].strip())

    if data_y == 'cd':
        legendLocation = 'upper left'

    plt.axis([graphSettings[key][x_min], graphSettings[key][x_max],
              graphSettings[key][y_min], graphSettings[key][y_max]])
    plt.xticks(np.arange(graphSettings[key][x_min],
                         graphSettings[key][x_max] + 0.00005, x_arranger), fontsize=labelsFontSize)
    plt.yticks(np.arange(graphSettings[key][y_min],
                         graphSettings[key][y_max] + 0.00005, y_arranger), fontsize=labelsFontSize)
    plt.xlabel(x_title, fontsize=fontSize)
    plt.ylabel(y_title, fontsize=fontSize)
    plt.grid(True)
    plt.legend(loc=legendLocation, fontsize=labelsFontSize)
    plt.savefig(fname=savingName)
    # plt.show()
