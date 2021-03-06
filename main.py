from disease_spread.rvalue_model import *
import subprocess as cmd
import pandas as pd
import pickle
import time
live_mode = True

# pull latest code from github
if live_mode:
    cp = cmd.run("git pull", check=True, shell=True)
    time.sleep(15)


# Check for new data. Abort if none
if live_mode:
    x_newdatacheck = rmodel_govuk()
    new_data = x_newdatacheck.check_todays_update()
    if new_data is False:
        raise Exception('No new data for '+str(pd.Timestamp.today().date())+'. Aborting')

# Run the model
x = run_govukmodel(save_output=live_mode,
                   dirname = './results/rvalue_model_' + str(pd.Timestamp.today().date()).replace('-', '_'))

if live_mode:
    time.sleep(15)

    # Specify folder to save the most recent model and plots
    dirname = './results/recent'

    # Save the output figures in a "recent"
    # folder for updating the readme page
    fig_plot = x.plot_model(return_figure=True, reference_level=1000)
    plt.savefig(dirname+'/forecast.png',dpi=1200)
    fig_cov = x.plot_covariance(return_figure=True)
    plt.savefig(dirname+'/correlation.png',dpi=500)


    # Plot the rolling r tracker
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig, ax1 = x.plot_r_estimate(fig, ax1)
    ax1.set_title('Rolling Reproduction Factor Calculation')

    xann = {'date':[pd.Timestamp(2020, 3, 23),
            pd.Timestamp(2020, 11, 5),
            pd.Timestamp(2021, 1, 2)],
            'label':['Lockdown 1','2','3']}
    idx = 1
    for date, lab in zip(xann['date'],xann['label']):
        if idx == 1:
            label = 'UK Lockdowns'
        else:
            label = None
        ax1.axvline(date,ls=':',label=label,color='purple')
        idx += 1

    #add uk return to school
    ax1.axvline(pd.Timestamp(2021, 3, 8),ls='--',color='r',label='Schools re-open')

    # restrictions lifted in sequence https://www.bbc.co.uk/news/explainers-52530518
    # stage 1 restrictions lifted # outdoor gardens (rule of 6)
    idx = 0
    for ts in [pd.Timestamp(2020, 6, 1),
               pd.Timestamp(2020, 12, 1),
               pd.Timestamp(2021, 3, 29),
               pd.Timestamp(2021, 4, 12),
               pd.Timestamp(2021, 5, 17),
               pd.Timestamp(2021, 6, 21)]:
        if idx == 0:
            ax1.axvline(ts,ls=':',color='r',label='Unlocking Stages')
        else:
            ax1.axvline(ts,ls=':',color='r',label=None)
        idx += 1



    plt.legend()
    plt.tight_layout()
    plt.savefig(dirname+'/rolling_r_plot.png',dpi=1000)


    # Save the model
    f = open(dirname + "/model.pkl", "wb")
    pickle.dump({'model': x}, f)
    f.close()

    # Commit results to github
    today_str = str(pd.Timestamp.today().date())
    cp = cmd.run("git add .", check=True, shell=True)
    message = "[ci skip] Results "+today_str
    cp = cmd.run(f"git commit -m '{message}'", check=True, shell=True)
    cp = cmd.run("git push -u origin master -f", check=True, shell=True)
