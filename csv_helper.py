import os
import csv

def write_to_csv(path, data):
    file = open(path,'a',newline='')
    writer = csv.writer(file)
    writer.writerow(data)
    file.close()