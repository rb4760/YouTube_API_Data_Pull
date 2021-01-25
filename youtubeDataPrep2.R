#Load the libraries that may be required
library("readxl") # used to read excel files
library("dplyr") # used for data munging 
library("caret") # used for various predictive models
library("class") # for using confusion matrix function
library("rpart.plot") # used to plot decision tree
library("rpart")  # used for Regression tree
library("glmnet") # used for Lasso and Ridge regression
library('NeuralNetTools') # used to plot Neural Networks
library("skimr") #used for skim() function to summarize the dataset 
library("tidyverse") # will allow us to use the read_csv() function w is better than read.csv
library("readr") # used to read csv files

#Load the file w/ Yuotube sentiment
initialtubeout_11_ <- read_csv("C:/Users/19178/Desktop/Capstone/initialtubeout (11).csv", col_names = FALSE)

#Assess the file contents
skim(initialtubeout_11_)

#Save the data as a datafraame
initialtubeout<- as.data.frame(initialtubeout_11_)

#Add the column names
colnames(initialtubeout)<-c("comments", "commentsId", "repliesCount", "likesCount", "viewerRating", "updatedAt", "videoId")

#Load the iMdb data set
Movie_List_v4 <- read_excel("C:/Users/19178/Desktop/Capstone/Movie_List_v4.xlsx", sheet = "Movie_List_v4")
movieList<-as.data.frame(Movie_List_v4)

#Pull in the relevant columns
movieList=movieList %>% select(c("videoId","imdb_id","title","release_date","imdbRating","youtube_trailer1"))
                        
#Merege the two data sets by videoId
initialtubeout <- as.data.frame(merge(initialtubeout, movieList, by="videoId"))

#Filter out the comments outsude of ReleaseDt+7 Obs. Window
initialtubeout$updatedAt<-as.Date(initialtubeout$updatedAt,format="%Y/%m/%d")
initialtubeout$date_diff <- as.Date(initialtubeout$updatedAt, format="%Y/%m/%d")-as.Date(initialtubeout$release_date, format="%Y/%m/%d")
initialtubeout <- initialtubeout %>% filter(date_diff <= 7)

#Save the Resulting file as .CSV
write.csv(initialtubeout,"relevant_youtube2.csv")