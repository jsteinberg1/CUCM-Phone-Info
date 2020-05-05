import sys, hashlib
from datetime import datetime

import logging
import sqlalchemy.orm.exc
from sqlalchemy.orm import Session, joinedload, contains_eager
from typing import List

from api.Config import config

from api.db.database import SessionLocal

from api.models import settings_management as models

logger = logging.getLogger('api')

def get_cucm_clusters(db: Session = SessionLocal()):
    results = db.query(models.CUCM_Cluster).all()

    db.close()

    for result in results:
        result.pd = config.key.decrypt(result.pd).decode()

    return results

def delete_cucm_cluster(id: int, db: Session = SessionLocal()):

    db.query(models.CUCM_Cluster).filter(models.CUCM_Cluster.id==id).delete()

    db.commit()
    db.close()


def delete_cucm_cluster_name(cluster_name: str, db: Session = SessionLocal()):

    db.query(models.CUCM_Cluster).filter(models.CUCM_Cluster.cluster_name==cluster_name).delete()

    db.commit()
    db.close()


def merge_cucm_cluster(cucm_cluster: models.CUCM_Cluster, db: Session = SessionLocal()):
    # write CA certificate file   
    cucm_cluster.pd = config.key.encrypt(cucm_cluster.pd.encode())

    db.merge(cucm_cluster)
    db.commit()
    db.close()



def get_all_cucm_users(db: Session = SessionLocal()):
    try:
        results = db.query(models.CUCM_Users).all()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

    db.close()
    
    return results


def merge_cucm_user(userid: str, db: Session = SessionLocal()):

    db.merge(models.CUCM_Users(userid=userid))

    db.commit()
    db.close()


def delete_cucm_user(userid: str, db: Session = SessionLocal()):
    try:
        db.query(models.CUCM_Users).filter(models.CUCM_Users.userid==userid).delete()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

    db.commit()
    db.close()


def get_all_settings(db: Session = SessionLocal()):
    try:
        results = db.query(models.Settings).all()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

    db.close()
    
    return results


def get_setting(name: str, db: Session = SessionLocal()):
    try:
        result = db.query(models.Settings).filter(models.Settings.name==name).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

    db.close()

    return result.value


def change_setting(name: str, value: str, db: Session = SessionLocal()):
    
    try:
        result = db.query(models.Settings).filter(models.Settings.name==name).one()
        result.value = value
    except sqlalchemy.orm.exc.NoResultFound:
        db.merge(models.Settings(name=name, value=value))

    db.commit()
    db.close()


def updatepw(old_password: str, new_password: str, db : Session = SessionLocal()):
    old_real_password_hash = get_setting(name='localadmin')
    old_supplied_password_hash = hashlib.sha512((old_password + str(config.salt)).encode()).hexdigest()
    
    if old_supplied_password_hash == old_real_password_hash:
        try:
            new_password_hash = hashlib.sha512((new_password + str(config.salt)).encode()).hexdigest()
            change_setting(name = 'localadmin', value=new_password_hash)
        except Exception as e:
            return "Password change failed"
        else:
            return "Password successfully changed"
    else:
        return "Current password does not match"
