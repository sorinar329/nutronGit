# ProductKG NutrOn

This repository contains the code for the website productkg.informatik.uni-bremen.de
In the following steps it will be explained how to run this application locally.

## Clone Repo and Install packages
First you will need to clone the repository.
After that you will need to install the required packages provided by "requirments.txt".
For this simply cd to your working directory, where you cloned the repo and execute:

`pip install -r requirments.txt`

## Change db_path
The standart db_path for this repository will always be

´db_path = '/var/www/nutron/user.db'´

since this is the path provided for the website.
If you want to run the application locally you will need to provide the path to the user.db database in your working directory
Normaly this will be

´db_path  = 'user.db'´

The changes need to be made in ´main.py´ and ´userDAO.py´

## Run the application
In order to run the application, after you did all the steps before, you will just need to run the main.py

## Contact
If you need any help regarding the code feel free to contact me at
sorin@uni-bremen.de or Sorenso1947#1534 on discord.
