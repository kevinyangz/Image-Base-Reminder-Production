import numpy as np
import os
import random

def Category_To_Int(CategoryAndLabel,label):
	return CategoryAndLabel[label]

def Listdir_not_Hidden(path):
	Category=[]
	for f in os.listdir(path):
		if not f.startswith('.'):
			Category.append(f)
	return Category 

def GetCategoryAndLabel(base_path): 
	CategoryAndLabel={}
	for index,item in enumerate(Listdir_not_Hidden(base_path)):
		CategoryAndLabel[item]=index
	return CategoryAndLabel

def GetLabelAndCategory(Category):
	LabelAndCategoryMapping={}
	for key, value in Category.items():
	 	LabelAndCategoryMapping[value]=key
	return LabelAndCategoryMapping
	 	
