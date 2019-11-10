from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_ALL, "")
import pytz

#def timer_

tz_irkutsk = pytz.timezone('Asia/Irkutsk') # Часовой пояс
print (tz_irkutsk)
weekday = ['пн','вт','ср','чт','пт','сб','вс']

now = datetime.now(tz_irkutsk)
year = int(now.strftime('%Y'))
month = int(now.strftime('%m'))
day = int(now.strftime('%d'))
h = int(now.strftime('%H'))
m = int(now.strftime('%M'))
s = int(now.strftime('%S'))
now = datetime(year, month, day,h, m, s) # Текущее время

print(now.strftime("%d %B %Y (%a)")) 

weekday_now = (now.strftime('%a')).lower()
print(weekday_now)

#====================Получить данные из БД==========================#
time_zan ='14:00' # Время занятия 
time_zan = time_zan.split(':')
weekday_zan = 'вс'  # День недели занятия
#=======================================================#

# Определяем сколько дней до ближайшего занятия
if int(time_zan[0])<=h and int(time_zan[1])<=m:
    k=8
else:
    print('зашло')
    f = False
    k=0
    for i in weekday:
    
        k+=1
        if i == weekday_now:
            f = True
            k=0
            k+=1
        if i == weekday_zan and f == True :
            break
        if i == 'вс' and k!=0:
            for j in weekday:
                k+=1
                if j == weekday_zan:
                    break


zanatie_date = now + timedelta(k-1)
year = int(zanatie_date.strftime('%Y'))
month = int(zanatie_date.strftime('%m'))
day = int(zanatie_date.strftime('%d'))
zanatie = datetime(year, month, day,int(time_zan[0]),int(time_zan[1])) # Дата и время ближайшего занятия

print(zanatie.strftime("%d %B %Y (%a)")) 

period = zanatie - now # Сколько осталось

mm, ss = divmod(period.seconds, 60)
hh, mm = divmod(mm, 60)
print('Осталось: {} д {} ч {} мин {} сек.'.format(period.days, hh, mm, ss))