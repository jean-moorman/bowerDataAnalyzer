import pandas as pd
import numpy as np
import os, re, pdb
import matplotlib.pyplot as plt
import seaborn as sns
#from statsmodels.stats.anova import AnovaRM
import statsmodels.formula.api as smf
import statsmodels.stats.multicomp as multi

#directories
cur_dir = os.getcwd()

data_dir = os.path.join(cur_dir, "masterSummarizedData_090619ZJ.xlsx")


'''Processing excel file:'''
xls = pd.ExcelFile(data_dir)
dfTotal = pd.read_excel(xls, "Total", index_col = 0)
f1Total = dfTotal[dfTotal.iloc[:, 0].str.contains('F1')]
parTotal = dfTotal[~dfTotal.iloc[:, 0].str.contains('F1')]

dfDaily = pd.read_excel(xls, "Daily", index_col = 0)
f1Daily = dfDaily[dfDaily.iloc[:, 0].str.contains('F1')]
parDaily = dfDaily[~dfDaily.iloc[:, 0].str.contains('F1')]

dfHourly = pd.read_excel(xls, "Hourly", index_col = 0)
f1Hourly = dfHourly[dfHourly.iloc[:, 0].str.contains('F1')]
parHourly = dfHourly[~dfHourly.iloc[:, 0].str.contains('F1')]

dfDailyAvg = pd.read_excel(xls, "Daily Averages", index_col = 0)
f1DailyAvg = dfDailyAvg[dfDailyAvg.iloc[:, 0].str.contains('F1')]
parDailyAvg = dfDailyAvg[~dfDailyAvg.iloc[:, 0].str.contains('F1')]

dfHourlyAvg = pd.read_excel(xls, "Hourly Averages", index_col = 0)
f1HourlyAvg = dfHourlyAvg[dfHourlyAvg.iloc[:, 0].str.contains('F1')]
parHourlyAvg = dfHourlyAvg[~dfHourlyAvg.iloc[:, 0].str.contains('F1')]

#remove controls
controls = ['MC10_1', 'TI3_1', 'CV9_1', 'MC6_3', 'TI1_1', 'TI8_1', 'CV14_1', 'CV10_2', 'MC11_1']
parDailyControls = parDaily.copy()
parHourlyControls = parHourly.copy()

parDaily = parDaily.set_index('projectID')
parHourly = parHourly.set_index('projectID')

parDaily.drop(labels = controls, inplace = True)
parHourly.drop(labels = controls, inplace = True)

parDaily.reset_index(inplace = True)
parHourly.reset_index(inplace = True)

f1_trial_names = [x for x in dfDaily.iloc[:, 0] if (x.find("F1") >= 0)]
#print('\nF1 Trials: ', set(f1_trial_names))

par_trial_names = [x for x in parDaily.iloc[:, 0] if (x.find("empty") < 0)]
#print('\n\nParental Trials: ', set(par_trial_names))


'''DataFrames:'''
dailyCols = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'] #days

#daily bower index
dailyBowersF1 = pd.DataFrame(columns = (['Trial'] + dailyCols))
dailyBowersPar = pd.DataFrame(columns = (['Trial'] + dailyCols))

#daily hourly bower index averages for building days only
hourlyAvgBowersF1 = pd.DataFrame(columns = (['Trial'] + dailyCols))
hourlyAvgBowersPar = pd.DataFrame(columns = (['Trial'] + dailyCols))

#daily ANOVA
dailyNova1 = pd.DataFrame(columns = ['Trial', 'Day', 'BowerIndex']) #one-way F1 daily

dailyNova2 = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #two-way F1 daily

dailyNova2Plus = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #two-way F1 + CV, TI, & MC daily

dailyNova2Minus = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #F1 pooled

dailyPooled = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #F1 and Pit pooled

dailyNova3 = pd.DataFrame(columns = ['Trial', 'Day', 'F1Bool', 'BowerIndex']) #two-way F1-pooled vs parental daily


#hourly averaged ANOVA
hourlyNova1 = pd.DataFrame(columns = ['Trial', 'Day', 'BowerIndex']) #one-way F1 daily hourly averages

hourlyNova2 = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #two-way F1 daily hourly averages

hourlyNova2Plus = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #two-way F1 + CV, TI, & MC daily hourly averages

hourlyNova2Minus = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #F1 pooled

hourlyPooled = pd.DataFrame(columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior']) #F1 and Pit pooled

hourlyNova3 = pd.DataFrame(columns = ['Trial', 'Day', 'F1Bool', 'BowerIndex']) #two-way F1-pooled vs parental daily hourly average

#hours
hourlyCols = ['Hour 1', 'Hour 2', 'Hour 3', 'Hour 4', 'Hour 5', 'Hour 6', 'Hour 7', 'Hour 8', 'Hour 9', 'Hour 10', 'Hour 11', 'Hour 12', 'Hour 13', 'Hour 14', 'Hour 15', 'Hour 16', 'Hour 17', 'Hour 18', 'Hour 19', 'Hour 20', 'Hour 21', 'Hour 22', 'Hour 23', 'Hour 24', 'Hour 25', 'Hour 26', 'Hour 27', 'Hour 28', 'Hour 29', 'Hour 30', 'Hour 31', 'Hour 32', 'Hour 33', 'Hour 34', 'Hour 35', 'Hour 36', 'Hour 37', 'Hour 38', 'Hour 39', 'Hour 40', 'Hour 41', 'Hour 42', 'Hour 43', 'Hour 44', 'Hour 45', 'Hour 46', 'Hour 47', 'Hour 48', 'Hour 49', 'Hour 50', 'Hour 51', 'Hour 52', 'Hour 53', 'Hour 54', 'Hour 55', 'Hour 56', 'Hour 57', 'Hour 58', 'Hour 59', 'Hour 60']

#For Manu
hourlyBowersF1 = pd.DataFrame(columns = (['Trial'] + hourlyCols))
hourlyBowersPar = pd.DataFrame(columns = (['Trial'] + hourlyCols))

#Volumes (useless)
dailyVolumesF1 = pd.DataFrame(columns = (['Trial'] + dailyCols))
dailyVolumesPar = pd.DataFrame(columns = (['Trial'] + dailyCols))
hourlyVolumesF1 = pd.DataFrame(columns = (['Trial'] + hourlyCols))
hourlyVolumesPar = pd.DataFrame(columns = (['Trial'] + hourlyCols))

hourLimit = 0


'''F1 Crosses:'''
for trial in set(f1_trial_names):

    '''Daily Processing:'''
    #initialize trialDaily
    trialDaily = f1Daily[f1Daily.iloc[:, 0].str.contains(trial)]
    trialDaily = trialDaily[['totalVolume', 'bowerIndex', 'bowerIndex_0.4', 'bowerIndex_0.8', 'bowerIndex_1.2']]

    #finds building start day and removes prior ones
    day = 1
    for index, row in trialDaily.iterrows(): #row = dfDaily.iloc[index, :]
        if (row['bowerIndex'] == 0 or pd.isnull(row['bowerIndex'])):
            trialDaily = trialDaily.iloc[1:, :]
            day += 1
            continue
        else:
            break

    #trims down to 5 days if necessary
    if (len(trialDaily.index) > 5):
        trialDaily = trialDaily.iloc[:5, :]
    #add bowerAvg column
    trialDaily['bowerAvg'] = trialDaily.loc[:, 'bowerIndex':'bowerIndex_1.2'].apply(np.mean, axis = 1) #should this go before trimming??


    '''Hourly Processing:'''
    #initialize trialHourly
    trialHourly = f1Hourly[f1Hourly.iloc[:, 0].str.contains(trial)]
    trialHourly = trialHourly[['totalVolume', 'bowerIndex', 'bowerIndex_0.2', 'bowerIndex_0.4', 'bowerIndex_0.8', 'Day']]
    #finds building start hour and removes those prior
    for index, row in trialHourly.iterrows(): #row = dfHourly.iloc[index, :]
        if row['Day'] <  day:
            trialHourly = trialHourly.iloc[1:, :] #gets rid of one hour at a time when wrong day
            continue
        if row['Day'] == day:
            if (row['bowerIndex'] == 0 or pd.isnull(row['bowerIndex'])):
                trialHourly = trialHourly.iloc[1:, :] #gets rid of one hour at a time when building hasn't started yet
                continue
            else:
                break

    #trims down hours to 5 days after building
    trialHourly = trialHourly[trialHourly['Day'] <= (day + 4)]
    #add bowerAvg column to trialHourly
    trialHourly['bowerAvg'] = trialHourly.loc[:, 'bowerIndex':'bowerIndex_0.8'].apply(np.mean, axis = 1) #should this go before trimming??


    '''Hourly Average Processing:'''
    #initialize trialHourlyAvg
    trialHourlyAvg = trialDaily.copy()
    trialHourlyAvg = trialHourlyAvg[['bowerAvg']]

    #hourly averaged for bower avg
    count = 0
    for ind, row in trialHourlyAvg.iterrows():
        if (row['bowerAvg'] == 0 or pd.isnull(row['bowerAvg'])):
            trialHourlyAvg.iloc[count]['bowerAvg'] = np.nan
        else:
            trialHourlyAvg.iloc[count]['bowerAvg'] = trialHourly[trialHourly['Day'] == (day + count)]['bowerAvg'].mean()
        count += 1

    '''Data Recording:'''
    #daily data
    dailyBowerDict = {dailyCols[i]: (trialDaily.iloc[i]['bowerAvg'] if i < trialDaily.shape[0] else np.nan) for i in range(5)}
    dailyBowerDict.update({'Trial': trial})
    dailyBowersF1 = dailyBowersF1.append(dailyBowerDict, ignore_index = True)

    #hourly average data
    hourlyAvgBowerDict = {dailyCols[i]: (trialHourlyAvg.iloc[i]['bowerAvg'] if i < trialDaily.shape[0] else np.nan) for i in range(5)}
    hourlyAvgBowerDict.update({'Trial': trial})
    hourlyAvgBowersF1 = hourlyAvgBowersF1.append(hourlyAvgBowerDict, ignore_index = True)


    #hourly data
    hourlyBowerDict = {hourlyCols[i]: (trialHourly.iloc[i]['bowerAvg'] if i < trialHourly.shape[1] else np.nan) for i in range(60)} #shape??
    hourlyBowerDict.update({'Trial': trial})
    hourlyBowersF1 = hourlyBowersF1.append(hourlyBowerDict, ignore_index = True)


    #Volumes (useless)
    dailyVolumeDict = {dailyCols[i]: (trialDaily.iloc[i]['totalVolume'] if i < trialDaily.shape[0] else np.nan) for i in range(5)}
    dailyVolumeDict.update({'Trial': trial})
    dailyVolumesF1 = dailyVolumesF1.append(dailyVolumeDict, ignore_index = True)

    hourlyVolumeDict = {hourlyCols[i]: (trialHourly.iloc[i]['totalVolume'] if i < trialHourly.shape[1] else np.nan) for i in range(60)}
    hourlyVolumeDict.update({'Trial': trial})
    hourlyVolumesF1 = hourlyVolumesF1.append(hourlyVolumeDict, ignore_index = True)

    #ANOVA chunks
    trialDays = trialDaily.shape[0]

    nova1Chunk = pd.DataFrame(np.nan, index = [int(x) for x in range(trialDays)], columns = ['Trial', 'Day', 'BowerIndex'])

    nova1Chunk['Trial'] = [trial] * trialDays
    nova1Chunk['Day'] = [int(x) for x in range(1, trialDays + 1)]
    nova1Chunk['BowerIndex'] = trialDaily['bowerAvg'].values

    nova2Chunk = pd.DataFrame(np.nan, index = [int(x) for x in range(trialDays)], columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior'])

    nova2Chunk['Trial'] = [trial] * trialDays
    nova2Chunk['Day'] = [int(x) for x in range(1, trialDays + 1)]
    nova2Chunk['Lineage'] = [trial[:5]] * trialDays
    nova2Chunk['BowerIndex'] = trialDaily['bowerAvg'].values
    nova2Chunk['Behavior'] = "Cross"

    nova2MinusChunk = nova2Chunk.copy()
    nova2MinusChunk['Lineage'] = 'F1'


    nova3Chunk = pd.DataFrame(np.nan, index = [int(x) for x in range(trialDays)], columns = ['Trial', 'Day', 'F1Bool', 'BowerIndex'])

    nova3Chunk['Trial'] = [trial] * trialDays
    nova3Chunk['Day'] = [int(x) for x in range(1, trialDays + 1)]
    nova3Chunk['F1Bool'] = ['F1' in trial] * trialDays
    nova3Chunk['BowerIndex'] = trialDaily['bowerAvg'].values

    hourlyNova1Chunk = nova1Chunk.copy()
    hourlyNova1Chunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    hourlyNova2Chunk = nova2Chunk.copy()
    hourlyNova2Chunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    hourlyNova2MinusChunk = nova2MinusChunk.copy()
    hourlyNova2MinusChunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    hourlyNova3Chunk = nova3Chunk.copy()
    hourlyNova3Chunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    dailyNova1 = pd.concat([dailyNova1, nova1Chunk], ignore_index = True)
    dailyNova2 = pd.concat([dailyNova2, nova2Chunk], ignore_index = True, sort = False)
    dailyNova2Plus = pd.concat([dailyNova2Plus, nova2Chunk], ignore_index = True, sort = False)
    dailyNova3 = pd.concat([dailyNova3, nova3Chunk], ignore_index = True)
    dailyNova2Minus = pd.concat([dailyNova2Minus, nova2MinusChunk], ignore_index = True)
    dailyPooled = pd.concat([dailyPooled, nova2MinusChunk], ignore_index = True)

    hourlyNova1 = pd.concat([hourlyNova1, hourlyNova1Chunk], ignore_index = True)
    hourlyNova2 = pd.concat([hourlyNova2, hourlyNova2Chunk], ignore_index = True, sort = False)
    hourlyNova2Plus = pd.concat([hourlyNova2Plus, hourlyNova2Chunk], ignore_index = True, sort = False)
    hourlyNova3 = pd.concat([hourlyNova3, hourlyNova3Chunk], ignore_index = True)
    hourlyNova2Minus = pd.concat([hourlyNova2Minus, hourlyNova2MinusChunk], ignore_index = True)
    hourlyPooled = pd.concat([hourlyPooled, hourlyNova2MinusChunk], ignore_index = True)


#print('nova1: \n', dailyNova1)
#print('\n\nnova2: \n', dailyNova2)
#print('\n\nnova2plus: \n', dailyNova3)


'''F1 Post-Processing:'''
#set index to trial name
dailyBowersF1 = dailyBowersF1.set_index('Trial')
hourlyAvgBowersF1 = hourlyAvgBowersF1.set_index('Trial')

hourlyBowersF1 = hourlyBowersF1.set_index('Trial')

dailyVolumesF1 = dailyVolumesF1.set_index('Trial')
hourlyVolumesF1 = hourlyVolumesF1.set_index('Trial')

#filter out zeros
dailyBowersF1[dailyBowersF1.iloc[:, :] == 0] = np.nan
hourlyAvgBowersF1[hourlyAvgBowersF1.iloc[:, :] == 0] = np.nan

hourlyBowersF1[hourlyBowersF1.iloc[:, :] == 0] = np.nan

dailyVolumesF1[dailyVolumesF1.iloc[:, :] == 0] = np.nan
hourlyVolumesF1[hourlyVolumesF1.iloc[:, :] == 0] = np.nan

#add mean rows
dailyBowersF1.loc['Mean'] = dailyBowersF1.mean()
hourlyAvgBowersF1.loc['Mean'] = hourlyAvgBowersF1.mean()

hourlyBowersF1.loc['Mean'] = hourlyBowersF1.mean()

dailyVolumesF1.loc['Mean'] = dailyVolumesF1.mean()
hourlyVolumesF1.loc['Mean'] = hourlyVolumesF1.mean()


#add std rows
dailyBowersF1.loc['STD'] = dailyBowersF1.iloc[:-1].std(skipna = True)
hourlyAvgBowersF1.loc['STD'] = hourlyAvgBowersF1.iloc[:-1].std(skipna = True)

hourlyBowersF1.loc['STD'] = hourlyBowersF1.iloc[:-1].std(skipna = True)

dailyVolumesF1.loc['STD'] = dailyVolumesF1.iloc[:-1].std(skipna = True)
hourlyVolumesF1.loc['STD'] = hourlyVolumesF1.iloc[:-1].std(skipna = True)

#drop columns with only nan
dailyBowersF1.dropna(axis = 1, how = 'all', inplace = True)
hourlyAvgBowersF1.dropna(axis = 1, how ='all', inplace = True)

hourlyBowersF1 = pd.concat((hourlyBowersF1.iloc[:, :50], hourlyBowersF1.iloc[:, 50:].dropna(axis = 1, how = 'all', inplace = False)), axis = 1)

dailyVolumesF1.dropna(axis = 1, how = 'all', inplace = True)
hourlyVolumesF1 = pd.concat((hourlyVolumesF1.iloc[:, :50], hourlyVolumesF1.iloc[:, 50:].dropna(axis = 1, how = 'all', inplace = False)), axis = 1)

hourLimit = hourlyVolumesF1.shape[1]

'''
print('\ndailyBowersF1: \n', dailyBowersF1)
print('\n\n\n')
print('\nhourlyAvgBowersF1: \n', hourlyAvgBowersF1)
'''

'''Parentals:'''
for trial in set(par_trial_names): #unique values

    '''Daily Processing:'''
    trialDaily = parDaily[parDaily.iloc[:, 0].str.contains(trial)]
    trialDaily = trialDaily[['totalVolume', 'bowerIndex', 'bowerIndex_0.4', 'bowerIndex_0.8', 'bowerIndex_1.2']]

    #finds building start day and removes prior ones
    day = 1
    for index, row in trialDaily.iterrows(): #row = dfDaily.iloc[index, :]
        if (row['bowerIndex'] == 0 or pd.isnull(row['bowerIndex'])):
            trialDaily = trialDaily.iloc[1:, :]
            day += 1
            continue
        else:
            break

    if (trialDaily.shape[0] < 5):
        for i in range(5 - trialDaily.shape[0]):
            trialDaily = trialDaily.append(pd.Series([np.nan]*5, index = ['totalVolume', 'bowerIndex', 'bowerIndex_0.4', 'bowerIndex_0.8', 'bowerIndex_1.2']), ignore_index = True)

    #trims down to 5 days if necessary
    if (len(trialDaily.index) > 5):
        trialDaily = trialDaily.iloc[:5, :]

    #add bowerAvg column
    trialDaily['bowerAvg'] = trialDaily.loc[:, 'bowerIndex':'bowerIndex_1.2'].apply(np.mean, axis = 1)


    '''Hourly Processing:'''
    trialHourly = parHourly[parHourly.iloc[:, 0].str.contains(trial)]
    trialHourly = trialHourly[['totalVolume', 'bowerIndex', 'bowerIndex_0.2', 'bowerIndex_0.4', 'bowerIndex_0.8', 'Day']]

    #finds building start hour and removes those prior
    for index, row in trialHourly.iterrows(): #row = dfDaily.iloc[index, :]
        if row['Day'] <  day:
            trialHourly = trialHourly.iloc[1:, :] #gets rid of one hour at a time when wrong day
            continue
        if row['Day'] == day:
            if (row['bowerIndex'] == 0 or pd.isnull(row['bowerIndex'])):
                trialHourly = trialHourly.iloc[1:, :] #gets rid of one hour at a time when building hasn't started yet
                continue
            else:
                break

    #trims down hours to 5 days after building
    trialHourly = trialHourly[trialHourly['Day'] <= (day + 4)]

    #add bowerAvg column
    trialHourly['bowerAvg'] = trialHourly.loc[:, 'bowerIndex':'bowerIndex_0.8'].apply(np.mean, axis = 1)


    '''Hourly Average Processing:'''
    #initialize trialHourlyAvg
    trialHourlyAvg = trialDaily.copy()
    trialHourlyAvg = trialHourlyAvg[['bowerAvg']]

    #hourly averaged for bower avg
    count = 0
    for ind, row in trialHourlyAvg.iterrows():
        if (row['bowerAvg'] == 0 or pd.isnull(row['bowerAvg'])):
            trialHourlyAvg.iloc[count]['bowerAvg'] = np.nan
        else:
            trialHourlyAvg.iloc[count]['bowerAvg'] = trialHourly[trialHourly['Day'] == (day + count)]['bowerAvg'].mean()
        count += 1


    '''Data Processing:'''
    #daily data
    dailyBowerDict = {dailyCols[i]: (trialDaily.iloc[i]['bowerAvg'] if i < trialDaily.shape[0] else np.nan) for i in range(5)}
    dailyBowerDict.update({'Trial': trial})
    dailyBowersPar = dailyBowersPar.append(dailyBowerDict, ignore_index = True)

    #hourly average data
    hourlyAvgBowerDict = {dailyCols[i]: (trialHourlyAvg.iloc[i]['bowerAvg'] if i < trialHourlyAvg.shape[0] else np.nan) for i in range(5)}
    hourlyAvgBowerDict.update({'Trial': trial})
    hourlyAvgBowersPar = hourlyAvgBowersPar.append(hourlyAvgBowerDict, ignore_index = True)


    #hourly data
    hourlyBowerDict = {hourlyCols[i]: (trialHourly.iloc[i]['bowerAvg'] if i < trialHourly.shape[0] else np.nan) for i in range(60)}
    hourlyBowerDict.update({'Trial': trial})
    hourlyBowersPar = hourlyBowersPar.append(hourlyBowerDict, ignore_index = True)


    #Volumes (useless)
    dailyVolumeDict = {dailyCols[i]: (trialDaily.iloc[i]['totalVolume'] if i < trialDaily.shape[0] else np.nan) for i in range(5)}
    dailyVolumeDict.update({'Trial': trial})
    dailyVolumesPar = dailyVolumesPar.append(dailyVolumeDict, ignore_index = True)

    hourlyVolumeDict = {hourlyCols[i]: (trialHourly.iloc[i]['totalVolume'] if i < trialHourly.shape[0] else np.nan) for i in range(60)}
    hourlyVolumeDict.update({'Trial': trial})
    hourlyVolumesPar = hourlyVolumesPar.append(hourlyVolumeDict, ignore_index = True)

    #ANOVA 2+
    trialDays = trialDaily.shape[0]

    nova2Chunk = pd.DataFrame(np.nan, index = [int(x) for x in range(trialDays)], columns = ['Trial', 'Day', 'Lineage', 'BowerIndex', 'Behavior'])

    nova2Chunk['Trial'] = [trial] * trialDays
    nova2Chunk['Day'] = [int(x) for x in range(1, trialDays + 1)]
    nova2Chunk['Lineage'] = [trial[:2]] * trialDays
    nova2Chunk['BowerIndex'] = trialDaily['bowerAvg'].values
    if (trial[:2] == 'CV' or trial[:2] == 'TI'):
        nova2Chunk['Behavior'] = 'Pit'
    else:
        nova2Chunk['Behavior'] = 'Castle'

    dailyPooledChunk = nova2Chunk.copy()
    if (trial[:2] == 'CV' or trial[:2] == 'TI'):
        dailyPooledChunk['Lineage'] = 'Pit'


    hourlyNova2Chunk = nova2Chunk.copy()
    hourlyNova2Chunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    hourlyPooledChunk = dailyPooledChunk.copy()
    hourlyPooledChunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    dailyNova2Plus = pd.concat([dailyNova2Plus, nova2Chunk], ignore_index = True, sort = False)
    dailyNova2Minus = pd.concat([dailyNova2Minus, nova2Chunk], ignore_index = True)
    dailyPooled = pd.concat([dailyPooled, dailyPooledChunk], ignore_index = True)

    hourlyNova2Plus = pd.concat([hourlyNova2Plus, hourlyNova2Chunk], ignore_index = True, sort = False)
    hourlyNova2Minus = pd.concat([hourlyNova2Minus, hourlyNova2Chunk], ignore_index = True)
    hourlyPooled = pd.concat([hourlyPooled, hourlyPooledChunk], ignore_index = True)

    #ANOVA3
    nova3Chunk = pd.DataFrame(np.nan, index = [int(x) for x in range(trialDays)], columns = ['Trial', 'Day', 'F1Bool', 'BowerIndex'])

    nova3Chunk['Trial'] = [trial] * trialDays
    nova3Chunk['Day'] = [int(x) for x in range(1, trialDays + 1)]
    nova3Chunk['F1Bool'] = ['F1' in trial] * trialDays
    nova3Chunk['BowerIndex'] = trialDaily['bowerAvg'].values

    hourlyNova3Chunk = nova3Chunk.copy()
    hourlyNova3Chunk['BowerIndex'] = trialHourlyAvg['bowerAvg'].values

    dailyNova3 = pd.concat([dailyNova3, nova3Chunk], ignore_index = True)
    hourlyNova3 = pd.concat([hourlyNova3, hourlyNova3Chunk], ignore_index = True)



'''Parental Post-Processing:'''
#set index to trial name
dailyBowersPar = dailyBowersPar.set_index('Trial')
hourlyAvgBowersPar = hourlyAvgBowersPar.set_index('Trial')

hourlyBowersPar = hourlyBowersPar.set_index('Trial')

dailyVolumesPar = dailyVolumesPar.set_index('Trial')
hourlyVolumesPar = hourlyVolumesPar.set_index('Trial')

#filter out zeros
dailyBowersPar[dailyBowersPar.iloc[:, :] == 0] = np.nan
hourlyAvgBowersPar[hourlyAvgBowersPar.iloc[:, :] == 0] = np.nan

hourlyBowersPar[hourlyBowersPar.iloc[:, :] == 0] = np.nan

dailyVolumesPar[dailyVolumesPar.iloc[:, :] == 0] = np.nan
hourlyVolumesPar[hourlyVolumesPar.iloc[:, :] == 0] = np.nan

#add mean rows
dailyBowersPar.loc['Mean'] = dailyBowersPar.mean()
hourlyAvgBowersPar.loc['Mean'] = hourlyAvgBowersPar.mean()

hourlyBowersPar.loc['Mean'] = hourlyBowersPar.mean()

dailyVolumesPar.loc['Mean'] = dailyVolumesPar.mean()
hourlyVolumesPar.loc['Mean'] = hourlyVolumesPar.mean()

#add std rows
dailyBowersPar.loc['STD'] = dailyBowersPar.iloc[:-1].std(skipna = True)
hourlyAvgBowersPar.loc['STD'] = hourlyAvgBowersPar.iloc[:-1].std(skipna = True)

hourlyBowersPar.loc['STD'] = hourlyBowersPar.iloc[:-1].std(skipna = True)

dailyVolumesPar.loc['STD'] = dailyVolumesPar.iloc[:-1].std(skipna = True)
hourlyVolumesPar.loc['STD'] = hourlyVolumesPar.iloc[:-1].std(skipna = True)

#drop columns with only nan
dailyBowersPar.dropna(axis = 1, how = 'all', inplace = True)
hourlyAvgBowersPar.dropna(axis = 1, how = 'all', inplace = True)

hourlyBowersPar = pd.concat((hourlyBowersPar.iloc[:, :50], hourlyBowersPar.iloc[:, 50:].dropna(axis = 1, how = 'all', inplace = False)), axis = 1)

dailyVolumesPar.dropna(axis = 1, how = 'all', inplace = True)
hourlyVolumesPar = pd.concat((hourlyVolumesPar.iloc[:, :50], hourlyVolumesPar.iloc[:, 50:].dropna(axis = 1, how = 'all', inplace = False)), axis = 1)


'''displaying data tables
print('Daily Bowers F1: \n', dailyBowersF1)
print('\n\n\n')
print('Daily Bowers Parentals: \n', dailyBowersPar)
print('\n\n\n')
print('Hourly Average Bowers F1: \n', hourlyAvgBowersF1)
print('\n\n\n')
print('Hourly Average Bowers Parentals: \n', hourlyAvgBowersPar)
'''


'''writing to excel file
with pd.ExcelWriter(os.path.join(cur_dir, 'stats.xlsx'), engine = "openpyxl") as writer:

    #dailyVolumesF1.to_excel(writer, sheet_name = 'dailyVolumes')
    dailyBowersF1.to_excel(writer, sheet_name = 'dailyBowers')
    #hourlyVolumesF1.to_excel(writer, sheet_name = 'hourlyVolumes')
    hourlyAvgBowersF1.to_excel(writer, sheet_name = 'hourlyAvgBowers')
    #dailyVolumesPar.to_excel(writer, sheet_name = 'dailyVolumes', startrow = 13) #this could be more general
    dailyBowersPar.to_excel(writer, sheet_name = 'dailyBowers', startrow = 13)
    #hourlyVolumesPar.to_excel(writer, sheet_name = 'hourlyVolumes', startrow = 13)
    hourlyAvgBowersPar.to_excel(writer, sheet_name = 'hourlyAvgBowers', startrow = 13)


with pd.ExcelWriter(os.path.join(cur_dir, 'novastats.xlsx'), engine = "openpyxl") as writer:

    dailyNova1.to_excel(writer, sheet_name = 'Nova1')
    dailyNova2.to_excel(writer, sheet_name = 'Nova2')
    dailyNova2Plus.to_excel(writer, sheet_name = 'Nova2+')
    dailyNova3.to_excel(writer, sheet_name = 'Nova3')
    hourlyNova1.to_excel(writer, sheet_name = 'Nova1', startcol = 5)
    hourlyNova2.to_excel(writer, sheet_name = 'Nova2', startcol = 6)
    hourlyNova2Plus.to_excel(writer, sheet_name = 'Nova2+', startcol = 6)
    hourlyNova3.to_excel(writer, sheet_name = 'Nova3', startcol = 6)

    writer.save()
'''


'''displaying nova tables
print(dailyNova1)
print()
print(hourlyNova1)
print('\n\n\n')
print(dailyNova2)
print()
print(hourlyNova2)
print('\n\n\n')
print(dailyNova2Plus)
print()
print(hourlyNova2Plus)
print('\n\n\n')
print(dailyNova3)
print()
print(hourlyNova3)
'''


#dropping nan rows for LME analysis
dailyNova1.dropna(axis = 0, how = 'any', inplace = True)
hourlyNova1.dropna(axis = 0, how = 'any', inplace = True)
dailyNova2.dropna(axis = 0, how = 'any', inplace = True)
hourlyNova2.dropna(axis = 0, how = 'any', inplace = True)
dailyNova2Plus.dropna(axis = 0, how = 'any', inplace = True)
hourlyNova2Plus.dropna(axis = 0, how = 'any', inplace = True)
dailyNova3.dropna(axis = 0, how = 'any', inplace = True)
hourlyNova3.dropna(axis = 0, how = 'any', inplace = True)


'''linear mixed effects analysis
md1D = smf.mixedlm("BowerIndex ~ Day", dailyNova1, groups = dailyNova1["Trial"])
mdf1D = md1D.fit(reml = False)
print("\nF1 Daily:\n", mdf1D.summary())

md1H = smf.mixedlm("BowerIndex ~ Day", hourlyNova1, groups = hourlyNova1["Trial"])
mdf1H = md1H.fit(reml = False)
print("\nF1 Daily Hourly Averages:\n", mdf1H.summary())

md2D = smf.mixedlm("BowerIndex ~ Day + Lineage + Day:Lineage", dailyNova2, groups = dailyNova2["Trial"])
mdf2D = md2D.fit(reml = False)
print("\nF1 (Lineage Split) Daily:\n", mdf2D.summary())

md2H = smf.mixedlm("BowerIndex ~ Day + Lineage + Day:Lineage", hourlyNova2, groups = hourlyNova2["Trial"])
mdf2H = md2H.fit(reml = False)
print("\nF1 (Lineage Split) Daily Hourly Averages:\n", mdf2H.summary())

md2DPlus = smf.mixedlm("BowerIndex ~ Day + Lineage + Day:Lineage", dailyNova2Plus, groups = dailyNova2Plus["Trial"])
mdf2DPlus = md2DPlus.fit(reml = False)
print("\nAll Trials (Lineage Split) Daily:\n", mdf2DPlus.summary())

md2HPlus = smf.mixedlm("BowerIndex ~ Day + Lineage + Day:Lineage", hourlyNova2Plus, groups = hourlyNova2Plus["Trial"])
mdf2HPlus = md2HPlus.fit(reml = False)
print("\nAll Trials (Lineage Split) Daily Hourly Averages:\n", mdf2HPlus.summary())

md3D = smf.mixedlm("BowerIndex ~ Day + F1Bool + Day:F1Bool", dailyNova3, groups = dailyNova3["Trial"])
mdf3D = md3D.fit(reml = False)
print("\nAll Trials (F1 vs Parental) Daily:\n", mdf3D.summary())

md3H = smf.mixedlm("BowerIndex ~ Day + F1Bool + Day:F1Bool", hourlyNova3, groups = hourlyNova3["Trial"])
mdf3H = md3H.fit(reml = False)
print("\nAll Trials (F1 vs Parental) Daily Hourly Averages:\n", mdf3H.summary())
'''


#only plotting first 4 days
hourlyNova2Plus = hourlyNova2Plus[hourlyNova2Plus['Day'] != 5]

hourlyNova2Minus = hourlyNova2Minus[hourlyNova2Minus['Day'] != 5]

hourlyPooled = hourlyPooled[hourlyPooled['Day'] != 5]

dailyNova2Plus = dailyNova2Plus[dailyNova2Plus['Day'] != 5]

dailyNova2Minus = dailyNova2Minus[dailyNova2Minus['Day'] != 5]

dailyPooled = dailyPooled[dailyPooled['Day'] != 5]



#displaying plots 2 at a time
sns.set(style = "darkgrid")
sns.set_palette("viridis_r")

dailySpeciesPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = dailyNova2Plus)
dailySpeciesPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Daily Species:")
dailySpeciesPlot.figure.savefig('dailySpecies.png')
#plt.show()

plt.figure(2) ###
hourlySpeciesPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = hourlyNova2Plus)
hourlySpeciesPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Hourly Species:")
hourlySpeciesPlot.figure.savefig('hourlySpecies.png')
plt.show()

plt.figure(3)
dailyMinusPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = dailyNova2Minus)
dailyMinusPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Daily F1 Pooled:")
dailyMinusPlot.figure.savefig('dailyF1Pooled.png')
#plt.show()

plt.figure(4) ###
hourlyMinusPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = hourlyNova2Minus)
hourlyMinusPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Hourly F1 Pooled:")
hourlyMinusPlot.figure.savefig('hourlyF1Pooled.png')
plt.show()

plt.figure(5) ###
dailyPooledPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = dailyPooled)
dailyPooledPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Daily Pooled:")
dailyPooledPlot.figure.savefig('dailyPooled.png')
#plt.show()

plt.figure(6) ###
hourlyPooledPlot = sns.lineplot(x = "Day", y = "BowerIndex", style = "Lineage", hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = hourlyPooled)
hourlyPooledPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Hourly Pooled:")
hourlyPooledPlot.figure.savefig('hourlyPooled.png')
plt.show()

plt.figure(7)
dailyIndividualsPlot = sns.lineplot(x = 'Day', y = 'BowerIndex', style = 'Trial', hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = dailyNova2Plus, dashes = False)
dailyIndividualsPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Daily Individuals:")
dailyIndividualsPlot.figure.savefig('dailyIndividuals.png')
#plt.show()

plt.figure(8)
hourlyIndividualsPlot = sns.lineplot(x = 'Day', y = 'BowerIndex', style = 'Trial', hue = 'Behavior', hue_order = ['Castle', 'Cross', 'Pit'], ci = 68, data = hourlyNova2Plus, dashes = False)
hourlyIndividualsPlot.set(xlabel = 'Time (Days)', ylabel = 'Bower Index')
plt.title("Hourly Individuals:")
hourlyIndividualsPlot.figure.savefig('hourlyIndividuals.png')
plt.show()



#To Do:

#include nonaveraged bowerindex in one vein

#For each metric, we want the daily, as well as the averaged hourly for building hours on building days only.
