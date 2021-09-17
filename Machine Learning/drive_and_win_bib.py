import math
import pandas as pd

def datacleaning_comment (data):
    data["ENGINE_LOAD"] = data["ENGINE_LOAD"].astype(str)
    data["ENGINE_LOAD"] = [x.replace('%','') for x in data["ENGINE_LOAD"]]
    data ["ENGINE_LOAD"] = [x.replace(',','.') for x in data ["ENGINE_LOAD"]]

    data["AmbientAirTemp"] = data["AmbientAirTemp"].astype(str)
    data["AmbientAirTemp"] = [x.replace('C','') for x in data["AmbientAirTemp"]]

    data["ThrottlePos"] = data["ThrottlePos"].astype(str)
    data["ThrottlePos"] = [x.replace('%','') for x in data["ThrottlePos"]]
    data ["ThrottlePos"] = [x.replace(',','.') for x in data ["ThrottlePos"]]
    data["zone"] = data["zone"].astype(str)
    return (data)

def convert_to_number (data):
    data['time'] =  pd.to_datetime(data['time'])
    data = data.convert_dtypes(convert_string=False)
    
    dataconv =  data.apply(pd.to_numeric ,errors="coerce")
    dataconv = dataconv.drop(['zone','time'],axis=1)
    dataconv['zone'] = data['zone']
    dataconv['time'] = data['time']
    data = dataconv
    print(data['zone'])
    return(data)


def Time_conv(time): # time est sous le format "jour/mois/année h:min"
    l=str(time).split(' ')  # time extraction
    time =l[-1].split(':') # extraire h et min
    time_converted=int(time[0])*3600+int(time[1])*60 + int(time[2]) # convertir en  sec
    print(time[0], time[1], time[2])
    
    return(time_converted)

def time_conv_list(trip):
    l=list()
    for temps in trip['time']:
        print("time conv", Time_conv(temps))
        l.append(Time_conv(temps)) # enregistrer les temps convertis dans une liste
    return(l)

def trip_segmentation(trip):
    l=list()
    for index in trip['time']:
        l.append(Time_conv(index)) # enregistrer les temps convertis dans une liste
    time_limits=list()
    time_limits.append(0)
    for index in range(len(l)-1): # parcourir la liste pour segmenter les trips
       
        if ((l[index+1]-l[index])>20): # si la difference en time entre deux valeurs successives depasse une min on sépare les trips
            time_limits.append(index)
            time_limits.append(index+1)# liste des indexs des différents trips
    time_limits.append(len(trip)-1)
    print("time trip limits : \n", time_limits)
    new_time_limits=list()
    w=(len(time_limits))
    for i in range(0,(w-1),2):

        if (time_limits[i+1]-time_limits[i] < 10): # si le trip contient mois que 10 valeurs on l élimine
            continue
        new_time_limits.append(time_limits[i])
        new_time_limits.append(time_limits[i+1])
    return(new_time_limits)



def infraction ( trip ):
    infractions_count=dict()
    #print(trip)
    try:
        #location=trip.iloc[:,0]
        #vitesse = trip.iloc[:,1]
        vitesse = trip['Speed']
        RPM = trip['RPM']

        Zone_urbaine =trip['urbaine']
        #print("zone urb", Zone_urbaine)
        Route_nat = trip['RouteNat']
        #Autoroute = trip['autoroute']
    except: # si les données ne correspondent pas affichier fichier non valide et quitter
        print("fichier non valide")
        quit()
    VMoy = vitesse.mean()
    RPMMoy = RPM.mean()
    VVar =sqrt(st.variance(vitesse))
    RPMVar =sqrt(st.variance(RPM))
    #print(location)
    
    # initiation des compteurs d'infractions
    count11 = 0
    count12 = 0
    count21=0
    count22=0
    count31=0
    count32=0
    count_f=0
        
    for i in range(len(trip)):  #size de tab

        z=int(trip['urbaine'][i])
        
        if z == 1:
            if vitesse[i] > 50 :
                if vitesse[i] < 50 + 30: #vitesse < 80
                    count11 = count11 +1
                if vitesse[i] >= 50 + 30 : #vitesse > 80
                    count12 = count12 +1
      
        elif int(Route_nat[i]) == 1 :  #outside urban
            if vitesse[i] > 90 :
                if vitesse[i] < 90 + 30: #vitesse < 120
                    count21 = count21 +1
                if vitesse[i] >= 90 + 30 : #vitesse > 120
                    count22 = count22 +1
                    
        else:
            if vitesse[i]>110: #highway
                if vitesse[i] < 110 + 30: #vitesse < 140
                    count31 = count31 +1
                if vitesse[i] >= 110 + 30 : #vitesse > 140
                    count32 = count32 +1
    #
    infractions_count['soft_infraction_zone1']=count11
    infractions_count['soft_infraction_zone2']=count21
    infractions_count['soft_infraction_zone3']=count31
    infractions_count['hard_infraction_zone1']=count12
    infractions_count['hard_infraction_zone2']=count22
    infractions_count['hard_infraction_zone3']=count32
    infractions_count['vitesse_moyenne']=VMoy
    infractions_count['variance_vitesse']=VVar
    infractions_count['RPM_moyenne']=RPMMoy
    infractions_count['variance_RPM']= RPMVar
    
    print("infractions", infractions_count)
    return infractions_count

def infraction_report(infraction_count):
    hard_count =0
    soft_count =0
    for i, k in inf_count.items():
        if re.search('soft', i):
            soft_count =soft_count + int(k)
        if re.search('hard', i):
            hard_count =hard_count + int(k)
    print('hard count: ', hard_count)
    print('soft_count: ', soft_count)
    #trip_score= ((hard_count * 10 + soft_count)/len(trip_test))
    trip_score= hard_count * 10 + soft_count 
    print("score =", trip_score)
    print("Evaluation globale:\n")
    if trip_score < 2:
        print("conduite normale")
    elif trip_score < 10:
        print("conduite agressive")
    else:
        print("conduite dangereuse")
    return(trip_score)

def del_unsignicant_trip(data, segs):
    trip_cleaned=data.copy(deep='False')
    #print(len(trip_cleaned))
    x =tuple()
    segments=list()
    for i in range(0,len(segs)-1,2):
        x=(segs[i], segs[i+1])
        segments.append(x) 
    print(segments)

    for i in range(len(segments)-1):
        if segments[i+1][0] - segments[i][1]==1:
            print("dropped segs", segments[i], segments[i+1])
            continue
        print(range(segments[i][1]+1, segments[i+1][0] ))
        print(trip_cleaned)
        trip_cleaned = trip_cleaned.drop(index=range(segments[i][1]+1, segments[i+1][0] ), inplace=False)

def getBearing (alt1, alt2, long1, long2):
        lat = math.fabs(alt1 - alt2)
        lng = math.fabs(long1 - long2)
        if (alt1 < alt2 and long1 < long2):
            return (math.degrees(math.atan2(lng,lat)));
        elif (alt1 >= alt2 and long1 < long2):
            return  ((90 - math.degrees(math.atan2(lng,lat))) + 90);
        elif (alt1 >= alt2 and long1 >= long2):
            return  (math.degrees(math.atan2(lng,lat)) + 180);
        elif (alt1 < alt2 and long1 >= long2):
            return  ((90 - math.degrees(math.atan2(lng,lat))) + 270);
        return -1;

def completing_missing_data(data):
    try:
        data_missing_v= data_missing_v.interpolate(method="cubic",limit=3)
    except:
        data['Speed'] = data['Speed'].astype('float')
        data_missing_v = data[missing_values_list]
        data_missing_v= data_missing_v.interpolate(method="cubic",limit=3)
    return (data_missing_v)

def removing_incomplete_raws(data):
    data = data.dropna()
    data = data.reset_index(drop=True)
    data.count()
    return (data)
