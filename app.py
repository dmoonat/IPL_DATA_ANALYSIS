import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
st.set_option('deprecation.showPyplotGlobalUse', False)

def main():

	@st.cache(persist=True)
	def load_data(file):
		data = pd.read_csv(file)
		df=pd.read_csv('data/matches.csv')
		df.drop('umpire3',inplace=True,axis=1)
		return data,df
	
	st.header("IPL Data Analysis(2008-2019)")
	datafile = 'data/deliveries.csv'
	df,df_matches = load_data(datafile)

	
	tasks = ["Overall", "Batsman", "Bowler","Teams Comparision"] #, "Fielder"
	select_task = st.selectbox("Analysis",tasks)

	Teams={
    'Royal Challengers Bangalore':'RCB', 
    'Sunrisers Hyderabad':'SRH',
       'Rising Pune Supergiant':'RPS',
    'Mumbai Indians':'MI',
       'Kolkata Knight Riders':'KKR', 
    'Gujarat Lions':'GL',
    'Kings XI Punjab':'KXIP',
       'Delhi Daredevils':'DD',
    'Chennai Super Kings':'CSK',
    'Rajasthan Royals':'RR',
       'Deccan Chargers':'DC',
    'Kochi Tuskers Kerala':'KTK',
    'Pune Warriors':'PW',
       'Rising Pune Supergiants':'RPS'
	}

	if select_task=="Teams Comparision":
		team1 = df_matches.team1.unique().tolist()
		choice = st.selectbox("Team1",team1)

		team2 = [i for i in team1 if i!=choice]
		choice1 = st.selectbox("Team2",team2)
		st.subheader(choice +'  vs  '+choice1)

		def comparison(team1,team2):
			compare=df_matches[((df_matches['team1']==team1)|(df_matches['team2']==team1))&\
			((df_matches['team1']==team2)|(df_matches['team2']==team2))]
			if st.checkbox("Data | Matches played",False):
				st.write(compare.reset_index(drop=True))
			ax=sns.countplot(x='season', hue='winner',data=compare)
			ax.set(ylim=(0, 5))
			st.pyplot()

		comparison(choice,choice1)

	elif select_task=="Batsman":
		batsman = df.batsman.unique().tolist()
		choice2 = st.selectbox("Batsman",batsman)

		filt=(df['batsman']==choice2)
		df_batsman=df[filt]

		
		st.write("Total No. of Fours:",len(df_batsman[df_batsman['batsman_runs']==4]))
		st.write("Total No. of Sixes:",len(df_batsman[df_batsman['batsman_runs']==6]))
		st.write("Total Runs:",df_batsman['total_runs'].sum())

		def count(df,runs):
			return len(df[df['batsman_runs']==runs])*runs

		slices=np.array([count(df_batsman,1),count(df_batsman,2),count(df_batsman,3),\
		count(df_batsman,4),count(df_batsman,6)])
		labels=['one','two','three','four','six']
		explode=[0,0,0,0.05,0.05]
		percent = 100. *slices/slices.sum() 
		legend = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, percent)]
		plt.pie(slices)#,explode=explode, autopct='%1.1f%%', pctdistance=0.6
		plt.title("Total runs contribution")
		plt.legend(legend, bbox_to_anchor=(-0.01, 1.), fontsize=8)
		st.pyplot()

		season=df_matches[['id','season']].merge(df_batsman, left_on = 'id', right_on = 'match_id', how = 'left').drop('id', axis = 1)
		season_grp = season.groupby('season')[['batsman_runs']].sum().reset_index()
		if st.checkbox("Data | Batsman runs across seasons",False):
			st.write(season_grp)

		nonzero = [i for i in season_grp.batsman_runs if i>0]
		season_grp.plot.bar(x='season',y='batsman_runs',label='Average across seasons {}'.format(int(np.mean(nonzero))))
		plt.xlabel("Seasons")
		plt.ylabel("Total runs")
		plt.xticks(rotation=0)
		# plt.yticks(ticks=season_grp['batsman_runs'])
		st.pyplot()

		df_batsman['dismissal_kind'].value_counts().plot.pie(title="Dismissal kind")
		st.pyplot()


	elif select_task=="Bowler":
		bowler = df.bowler.unique().tolist()
		bowler = bowler[2:]+bowler[0:2]
		choice3 = st.selectbox("Bowler",bowler)

		filt=(df['bowler']==choice3)
		df_bowler=df[filt].reset_index(drop=True)
		# st.write(df_bowler)
		wks=df_bowler.player_dismissed.count()
		st.write("Total No. of wickets:",wks)
		
		season=df_matches[['id','season']].merge(df_bowler, left_on = 'id', right_on = 'match_id', how = 'left').drop('id', axis = 1)
		season_grp = season.groupby('season')[['player_dismissed']].count().reset_index()
		season_grp.plot.bar(x='season',y='player_dismissed',label='wickets')
		plt.xlabel("Seasons")
		plt.ylabel("No. of wickets")
		plt.xticks(rotation=0)
		# plt.yticks(ticks=season_grp['player_dismissed'])
		# st.bar_chart(season_grp['player_dismissed'])
		# sns.barplot(data=season_grp,x='season',y='player_dismissed')
		# plt.show()
		st.pyplot()

		df_bowler['dismissal_kind'].value_counts().plot.pie()
		plt.tight_layout()
		st.pyplot()
		st.write("Total deliveries:",len(df_bowler))
		st.write("Total wide deliveries:",df_bowler.wide_runs.sum())
		st.write("Total noball deliveries:",df_bowler.noball_runs.sum())
		st.write("Total extra runs:",df_bowler.extra_runs.sum())

	elif select_task=="Fielder":
		fielder = df.fielder.dropna().unique().tolist()
		choice4 = st.selectbox("Fielder",fielder)

		filt=(df['fielder']==choice4)
		df_bowler=df[filt]

	else:
		df_copy = df.copy()
		df_copy['batting_team']=df['batting_team'].map(Teams)
		df_copy['bowling_team']=df['bowling_team'].map(Teams)

		season=df_matches[['id','season']].merge(df_copy, left_on = 'id', right_on = 'match_id', how = 'left').drop('id', axis = 1)
		season_grp = season.groupby('season')[['total_runs']].sum().reset_index()

		avg_runs=df_matches.groupby(['season'])['id'].count().reset_index().rename(columns={'id':'matches'})
		avg_runs_per_season=pd.concat([avg_runs,season_grp.iloc[:,1]],axis=1)
		avg_runs_per_season['avg_runs']=avg_runs_per_season['total_runs']/avg_runs_per_season['matches']
		# avg_runs_per_season.set_index('season',inplace=True)

		st.write('Total Matches Played:',df_matches.shape[0])

		if st.checkbox("Data | Across seasons",False):
			st.write(avg_runs_per_season)

		
		sns.countplot(df_matches['season'])
		plt.xticks(rotation=45)
		plt.tight_layout()
		st.pyplot()

		sns.barplot(x='season',y='total_runs',data=season_grp)
		plt.xticks(rotation=45)
		plt.tight_layout()
		st.pyplot()

		sns.lineplot(x='season',y='avg_runs',data=avg_runs_per_season)
		plt.xticks(ticks=avg_runs_per_season.season,rotation=45)
		plt.tight_layout()
		st.pyplot()

		sns.countplot(x='season',hue='toss_decision',data=df_matches)
		plt.xticks(rotation=45)
		plt.tight_layout()
		st.pyplot()
		
		high_scores=df_copy.groupby(['match_id', 'inning','batting_team','bowling_team'])['total_runs'].sum().reset_index()
		


		runs=df_copy.groupby(['match_id','inning','batting_team'])[['total_runs']].sum().reset_index()
		runs.drop('match_id',axis=1,inplace=True)

		inning1=runs[runs['inning']==1]
		inning2=runs[runs['inning']==2]

		
		st.write("Score Distribution For Teams by Innings")
		
		if st.checkbox("Innings1 Score(Target) statistics",False,key=1):
			st.write(inning1.groupby('batting_team')['total_runs'].agg(['min','max','mean']).rename(columns={'min':'Minimum score',\
				'max':'Maximum score','mean':'Average score'}))

			score200 = inning1[inning1['total_runs']>=200]

			if st.checkbox("Boxplot",False,key=1):
				sns.boxplot(x='batting_team',y='total_runs',data=inning1)
				plt.title('Inning1 score')
				plt.tight_layout()
				st.pyplot()

			sns.countplot(score200['batting_team'])
			plt.title('No. of times Teams scored >200runs in Innings1')
			plt.tight_layout()
			st.pyplot()

		if st.checkbox("Innings2 Score(Run chase) statistics",False,key=2):
			st.write(inning2.groupby('batting_team')['total_runs'].agg(['min','max','mean']).rename(columns={'min':'Minimum score',\
				'max':'Maximum score','mean':'Average score'}))

			score200 = inning2[inning2['total_runs']>=200]

			if st.checkbox("Boxplot",False,key=2):
				sns.boxplot(x='batting_team',y='total_runs',data=inning2)
				plt.title('Inning2 score')
				plt.tight_layout()
				st.pyplot()

			sns.countplot(score200['batting_team'])
			plt.title('No. of times Teams scored >200runs in Innings2')
			plt.tight_layout()
			st.pyplot()



if __name__ == '__main__':
	main()