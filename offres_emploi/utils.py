import datetime
import pandas as pd

def dt_to_str_iso(dt):
    """
    Convert a datetime.datetime object to a string respecting the ISO-8601 format 
    Will raise ValueError if type not appropriate

    :param dt: The datetime object to convert
    :type dt: datetime.datetime 
    
    :returns: ISO 8601 formatted string
    :rtype: str       
    """
    iso_format = "%Y-%m-%dT%H:%M:%SZ"
    if isinstance(dt, datetime.datetime):
        s = dt.strftime(iso_format)
        return s
    else:
        raise ValueError("Arg 'dt' should be of class 'datetime.datetime'")


def filters_to_df(filters):
    """
    :param filters: The list of the filters available through "filtresDisponibles" key
    :type filters: list
    
    :rtype: pandas.DataFrame
    :returns: A pandas.DataFrame of the filters (that is more suitable to analysis)

    """
    dics = [{x["filtre"]: x["agregation"]} for x in filters]
    l = []
    for dic in dics:
        flat_dic = [
            dict(
                filtre=key,
                valeur_possible=x["valeurPossible"],
                nb_resultats=x["nbResultats"],
            )
            for (key, value) in dic.items()
            for x in value
        ]
        l.extend(flat_dic)
    df = pd.DataFrame(l)
    return df
