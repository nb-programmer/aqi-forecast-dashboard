
from prediction.dbaccess import db, models

import argparse
import os

def initialize_models():
    '''
    Makes sure required tables exist
    '''
    db.database.create_tables([models.AQI, models.Forecast], safe=True)

def initialize_data():
    with db.database:
        models.AQI.truncate_table()
        models.Forecast.truncate_table()
        #restore_csv("models/pcb_dataset_2017-2021.csv")

def dump_models(path : os.PathLike):
    pass

def restore_csv(path : os.PathLike):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reinit", action="store_true", help="Truncate and restore default data. WARNING! This will remove all data from the database that exists!")
    parser.add_argument("-d", "--dump", help="Dump all models into CSV file(s)")
    parser.add_argument("-y", dest='silent', action="store_true", help="Don't prompt inputs for confirmation")
    parser.add_argument("--nocreate", action="store_true", help="Don't try to create models as tables into the database")

    args = parser.parse_args()
    
    #Init database object
    db._load_database(None, db._db)
    
    if not args.nocreate:
        initialize_models()

    if args.reinit:
        is_proceed = False
        if args.silent:
            is_proceed = True
        else:
            i = input("\nWARNING! Re-initializing means all data will be deleted and default data will be restored.\nYou sure you want to proceed?[Y/n]> ")
            if i.lower()[0] == 'y':
                is_proceed = True
                print("Proceeding...")
            elif i.lower()[0] == 'n':
                is_proceed = False
                print("Not performing re-initialization")
        
        if is_proceed:
            initialize_data()
        
