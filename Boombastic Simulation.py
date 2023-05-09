import time
import mysql.connector
import numpy as np
import threading

cnx = mysql.connector.connect(user="root",
                              password="1477Mmdvddm.",
                              host="127.0.0.1",
                              database="boombastic")
cursor = cnx.cursor()


# defining structures needed:

# classes:


class Festival:
    def __init__(self, stages, areas, campings, checkin):
        # 9 possible locations
        self.stages = stages

        self.areas = areas

        self.campings = campings

        self.checkin = checkin




class Attendee:
    def __init__(self, id, camping, festival):
        self.id = id
        self.camping = camping  # camping can be 0 (no camping), (1) camping, (2) glamping
        self.checked = False
        self.festival = festival
        self.location = self.festival.campings[0]
        self.previous_location = None
        self.arrived = round(time.time() - t0,2)

    def run(self):
        if self.camping:
            t_sleep = (100) + np.random.uniform(0, 20)  # time till check-in
            time.sleep(t_sleep)

        else:
            t_sleep = (155) + np.random.uniform(0, 35)
            # this is an assumption (people with no camping have to come between 3:30pm and 8pm)
            time.sleep(t_sleep)

        with self.festival.checkin.lock:
            self.festival.checkin.queue.append(self)
        while not self.checked:
            time.sleep(0.001)



        while time.time() - t0 < 720 + 160:
            self.previous_location = self.location
            if self.camping == 0:  # NO CAMPING
                p = np.array([area.probability for area in
                              self.festival.stages + self.festival.areas + [self.festival.campings[0]]])
                p = p / np.sum(p)
                self.location = np.random.choice(self.festival.stages + self.festival.areas +[self.festival.campings[0]],
                                                 p=p)
            elif self.camping == 1:  # camping
                p = np.array([area.probability for area in
                              self.festival.stages + self.festival.areas + [self.festival.campings[1]]])
                p = p / np.sum(p)
                self.location = np.random.choice(self.festival.stages + self.festival.areas + [self.festival.campings[1]],
                                                 p=p)
            elif self.camping == 2:  # glamping
                p = np.array([area.probability for area in
                              self.festival.stages + self.festival.areas + [self.festival.campings[2]]])
                p = p / np.sum(p)
                self.location = np.random.choice(self.festival.stages + self.festival.areas + [self.festival.campings[2]],
                                                 p=p)


            if not self.location == self.previous_location:
                query = "INSERT INTO attendees (id, arrived, moved, location) VALUES (%s, %s, %s,%s)"  #inserting every action of each attendee
                values = (self.id, self.arrived, round(time.time() - t0, 2), self.previous_location.name)
                with sql_lock:
                    cursor.execute(query, values)
                    cnx.commit()
                self.arrived = time.time() - t0


            if type(self.location) == Stage: # This is to prevent people from being in the stage when the day has finished
                if self.location.artist == "Prohibited":
                    self.location = self.festival.campings[self.camping]
                    if self.location.name == 'Home':
                        t1 = time.time() - t0
                        if (t1 % 240 > 20) and (t1 % 240 < 155):
                            t_sleep = ((t1 // 240) * 240 + 155) - t1
                    else:
                        t1 = time.time() - t0
                        if (t1 % 240 > 20) and (t1 % 240 < 100):
                            t_sleep = ((t1 // 240) * 240 + 100) - t1
                    query = "INSERT INTO attendees (id, arrived, moved, location) VALUES (%s, %s, %s,%s)"
                    values = (self.id, self.arrived, round(time.time() - t0, 2), self.previous_location.name)
                    with sql_lock:
                        cursor.execute(query, values)
                        cnx.commit()
                    self.arrived = time.time() - t0
                    time.sleep(t_sleep)
                    continue

                else:
                    if self.location.artist:
                        t_sleep = (self.location.next_change + np.random.uniform(1.5,2.5)) - (time.time()-t0)
                        if t_sleep <0:
                            t_sleep = 1
                    else:
                        if self.location.artist_list:
                            t_sleep = self.location.artist_list[0][1] - (time.time()-t0)
                            if t_sleep < 0:
                                t_sleep=1
                        else:
                            break
            else:
                if self.location.name in ["Camping", "Glamping"]:
                    t1 = time.time() - t0
                    if (t1 % 240 > 20) and (t1 % 240 < 100):
                        t_sleep = ((t1 // 240) * 240 + 100) - t1
                    else:
                        t_sleep = self.location.minimum_stay + np.random.uniform(0, 12.5)
                elif self.location.name in ['Food Truck 1', 'Food Truck 2']:
                    t_sleep = self.location.minimum_stay + np.random.uniform(0, 0.5)
                elif self.location.name == 'WC':
                    t_sleep = self.location.minimum_stay + np.random.uniform(0, 0.75)
                elif self.location.name == 'Home':
                    t1 = time.time() - t0
                    if (t1 % 240 > 20) and (t1 % 240 < 155):
                        t_sleep = ((t1 // 240) * 240 + 155) - t1


            time.sleep(t_sleep)





class Zone:
    def __init__(self, name, minimum_stay, schedule):
        self.capacity = 100
        self.minimum_stay = minimum_stay
        self.name = name
        self.probability = None
        self.schedule = schedule

    def run(self):
        current = self.schedule.pop(0)
        self.probability = current[2]
        while time.time() - t0 < 720+160:
            if time.time() - t0 > current[1]:
                if self.schedule:
                    current = self.schedule.pop(0)
                    self.probability = current[2]
                else:
                    self.probability = 0
                    break


class Stage:
    def __init__(self, name, artist_list):
        self.artist_list = artist_list
        self.artist = None
        self.name = name
        self.next_change = None
        self.probability = 0.00

    def run(self):
        global stage_table_lock
        current = self.artist_list.pop(0)
        start = round(time.time() - t0,2)
        self.probability = current[3]
        self.artist = current[2]
        self.next_change = current[1]

        while time.time() - t0 < 720+160:
            if time.time() - t0 > current[1]:
                query = "INSERT INTO stages (location,  artist, start, finish) VALUES (%s, %s, %s, %s)"
                values = (self.name, self.artist,start, round(time.time()-t0,2))
                print("Change in Stage: ", values)
                with sql_lock:
                    cursor.execute(query, values)
                    cnx.commit()
                if self.artist_list:
                    current = self.artist_list.pop(0)
                    start = round(time.time() - t0,2)
                    self.probability = current[3]  # 4th element of list
                    self.artist = current[2]
                    self.next_change = current[1]
                else:
                    self.probability = 0
                    break


class Checkin:
    def __init__(self):
        self.lock = threading.Lock()
        self.queue = []
        self.attendees_checked_in = 0

    def run(self):
        while self.attendees_checked_in < 100:
            if self.queue:
                with self.lock:
                    checking_in = self.queue.pop(0)
                    checking_in.checked = True
                self.attendees_checked_in +=1
                print("Checked in: ",self.attendees_checked_in)



# schedule:

artists_schedule_negrita = [  # día 1
    [0, 180, None, 0],
    [180, 185, None, 0.2],
    [185, 195, 'Enol', 0.2],
    [195, 200, None, 0.7],
    [200, 210, 'Emilia', 0.7],
    [210, 225, None, 0.9],
    [225, 235, 'C. Tangana', 1.0],
    [235, 265, None, 0.00],
    [265, 275, 'Snow Tha Product', 0.00],
    [275, 170 + 240, "Prohibited", 0.0],
    # día 2
    [170 + 240, 175 + 240, None, 0.1],
    [175 + 240, 185 + 240, 'Xavibo', 0.1],
    [185 + 240, 185 + 240, None, 0.6],
    [185 + 240, 200 + 240, 'Delaossa', 0.7],
    [200 + 240, 205 + 240, None, 0.7],
    [205 + 240, 215 + 240, 'Eladio Carrion', 0.8],
    [215 + 240, 225 + 240, None, 0.7],
    [225 + 240, 240 + 240, 'Nathy Peluso', 0.9],
    [240 + 240, 250 + 240, None, 0.2],
    [250 + 240, 265 + 240, 'Ayax y Prox', 0.2],
    [265 + 240, 275 + 240, None, 0.2],
    [275 + 240, 287.5 + 240, 'Recycled J', 0.4],
    [287.5 + 240, 175 + 480,'Prohibited', 0.0],
    # día 3
    [175 + 480, 180 + 480, None, 0.01],  # para que vengan paulatinamente
    [180 + 480, 190 + 480, 'Jaime Lorente', 0.3],
    [190 + 480, 195 + 480, None, 0.1],
    [195 + 480, 205 + 480, 'Ptazeta', 0.2],
    [205 + 480, 210 + 480, None, 0.6],
    [210 + 480, 220 + 480, 'Morad', 0.6],
    [220 + 480, 230 + 480, None, 0.7],
    [230 + 480, 240 + 480, 'Nicki Nicole', 0.8],
    [240 + 480, 250 + 480, None, 0.00],
    [250 + 480, 265 + 480, 'HDLR', 0.01],
    [265 + 480, 275 + 480, None, 0.8],
    [275 + 480, 285 + 480, 'Bizarrap', 0.8],
    [285 + 480, 290 + 480, None, 0.3],
    [290 + 480, 310 + 480, 'Bresh', 0.4],
    [310 + 480, 160 + 720, "Prohibited", 0.0],
]

artists_schedule_aguila = [  # día 1
    [0, 170, None, 0.0],
    [170, 175, None, 0.2],
    [175, 182.5, 'Victxoria Txrmenta', 0.2],
    [182.5, 190, None, 0.3],
    [190, 200, 'Sofia Ellar', 0.5],
    [200, 205, None, 0.8],
    [205, 215, 'Taburete', 0.7],
    [215, 220, None, 0.01],
    [220, 230, 'Rojuu', 0.1],
    [230, 235, None, 0.5],
    [235, 250, 'Beret', 0.7],
    [250, 255, None, 0.4],
    [255, 265, 'Ana Mena', 0.5],
    [265, 270, None, 0.5],
    [270, 280, 'Don Patricio', 0.7],
    [280, 295, 'DJ Nano', 0.2],
    [295, 180 + 240, "Prohibited", 0.0],
    # día 2
    [180 + 240, 185 + 240, None, 0.2],
    [185 + 240, 195 + 240, 'Paula Cendejas', 0.2],
    [195 + 240, 200 + 240, None, 0.4],
    [200 + 240, 210 + 240, 'Chema Rivas', 0.5],
    [210 + 240, 215 + 240, None, 0.3],
    [215 + 240, 227.5 + 240, 'Juancho Marques', 0.3],
    [227.5 + 240, 237.5 + 240, None, 0.4],
    [237.5 + 240, 250 + 240, 'Fernandocosta', 0.5],
    [250 + 240, 260 + 240, None, 0.5],
    [260 + 240, 275 + 240, 'Funzo y Baby Loud', 0.6],
    [275 + 240, 280 + 240, None, 0.3],
    [280 + 240, 300 + 240, 'Bresh', 0.2],
    [300 + 240, 170 + 480, "Prohibited", 0.0],
    # día 3
    [170 + 480, 175 + 480, None, 0.2],
    [175 + 480, 185 + 480, 'Dudi', 0.2],
    [185 + 480, 190 + 480, None, 0.4],
    [190 + 480, 200 + 480, 'Alvaro de Luna', 0.4],
    [200 + 480, 205 + 480, None, 0.5],
    [205 + 480, 215 + 480, 'Arnau Griso', 0.6],
    [215 + 480, 220 + 480, None, 0.01],
    [220 + 480, 235 + 480, 'Hens', 0.01],
    [235 + 480, 240 + 480, None, 0.2],
    [240 + 480, 255 + 480, 'Marlon', 0.4],
    [255 + 480, 265 + 480, None, 0.8],
    [265 + 480, 275 + 480, 'Bad Gyal', 0.9],
    [275 + 480, 285 + 480 + 480, None, 0.4],
    [285 + 480, 295 + 480, 'RVFV', 0.5],
    [295 + 480, 160 + 720, "Prohibited", 0]
]

artists_schedule_jager = [[0, 170, None, 0.0],  # tbd
                          [170, 185, 'Blvck Seal', 0.2],
                          [185, 195, None, 0.1],
                          [195, 205, 'Dj Blando', 0.1],
                          [205, 215, None, 0.2],
                          [215, 225, 'Walls', 0.3],
                          [225, 235, None, 0.01],
                          [235, 245, 'Marc Seguí', 0.4],
                          [245, 260, None, 0.2],
                          [260, 270, 'Zzoilo', 0.3],
                          [270, 295, 'Pauli di The Otter Gang', 0.05],
                          [295, 165 + 240, "Prohibited", 0.0],
                          # día 2
                          [165 + 240, 170 + 240, None, 0.1],
                          [170 + 240, 190 + 240, 'Blvck Seal', 0.2],
                          [190 + 240, 195 + 240, None, 0.2],
                          [195 + 240, 205 + 240, 'Foyone', 0.2],
                          [205 + 240, 210 + 240, None, 0.1],
                          [210 + 240, 220 + 240, 'Nobeat', 0.2],
                          [220 + 240, 225 + 240, None, 0.05],
                          [225 + 240, 235 + 240, 'Lionware', 0.2],
                          [235 + 240, 240 + 240, None, 0.05],
                          [240 + 240, 250 + 240, 'Fusanocta', 0.2],
                          [250 + 240, 255 + 240, None, 0.1],
                          [255 + 240, 265 + 240, 'Blake', 0.2],
                          [265 + 240, 275 + 480, None, 0.05],
                          [275 + 240, 285 + 240, 'Stereocode', 0.06],
                          [285 + 240, 300 + 240, 'Michenlo', 0.04],
                          # día 3
                          [300 + 240, 165 + 480, "Prohibited", 0.0],
                            [165 + 480, 170 + 480, None, 0.1],
                          [170 + 480, 185 + 480, 'Blvck Seal', 0.2],
                          [185 + 480, 190 + 480, None, 0.5],
                          [190 + 480, 200 + 480, 'Aron', 0.7],
                          [200 + 480, 205 + 480, None, 0.1],
                          [205 + 480, 215 + 480, 'Aleesha', 0.2],
                          [215 + 480, 225 + 480, None, 0.1],
                          [225 + 480, 235 + 480, 'Dani Fdez', 0.2],
                          [235 + 480, 240 + 480, None, 0.1],
                          [240 + 480, 250 + 480, 'Rayden', 0.1],
                          [250 + 480, 255 + 480, None, 0.4],
                          [255 + 480, 265 + 480, 'Nil Moliner', 0.6],
                          [265 + 480, 270 + 480, None, 0.2],
                          [270 + 480, 280 + 480, 'Costa', 0.3],
                          [280 + 480, 285 + 720, None, 0.1],
                          [285 + 480, 295 + 480, 'Zetazen', 0.1],
                          [295 + 480, 310 + 480, 'Pauli di The Otter Gang', 0.1],
                          [310 + 480, 160 + 720, "Prohibited", 0]
                          ]

schedule_food_truck = [[0, 120, 0],
                       [120, 135, 0.05],
                       [135, 165, 0.03],
                        [165, 190, 0.005],
                       [190, 200, 0.001],
                       [200, 220, 0.02],
                       [220, 240, 0.075],
                       [0 + 240, 120 + 240, 0.0],
                       [120 + 240, 135 + 240, 0.05],
                       [135 + 240, 165 + 240, 0.005],
                       [165 + 240, 190 + 240, 0.001],
                       [190 + 240, 200 + 240, 0.01],
                       [200 + 240, 220 + 240, 0.02],
                       [220 + 240, 240 + 240, 0.075],
                       [0 + 480, 120 + 480, 0.0],
                       [120 + 480, 135 + 480, 0.05],
                       [135 + 480, 165 + 480, 0.005],
                       [165 + 480, 190 + 480, 0.001],
                       [190 + 480, 200 + 480, 0.01],
                       [200 + 480, 220 + 480, 0.02],
                       [220 + 480, 240 + 480, 0.075],
                       [240+480, 160 +720, 0.0]
                       ]

schedule_wc = [[0, 120, 0.00],
               [120, 200, 0.02],
               [200, 240, 0.01],
               [0 + 240, 120 + 240, 0.0],
               [120 + 240, 200 + 240, 0.02],
               [200 + 240, 240 + 240, 0.01],
               [0 + 480, 120 + 480, 0.00],
               [120 + 480, 200 + 480, 0.02],
               [200 + 480, 240 + 480, 0.01],
                [480 + 240, 120 + 720, 0.00],
                [120 + 720, 720 + 160, 0.00],
               ]

schedule_home = [[0, 155, 0.05],
                 [155, 260, 0],
                 [260, 275, 0.2],
                 [275, 295, 0.6],
                 [295, 240 + 155, 1.0],
                 [155 + 240, 260 + 240, 0],
                 [260 + 240, 275 + 240, 0.2],
                 [275 + 240, 295 + 240, 0.6],
                 [300 + 240, 480 + 155, 1],
                 [155 + 480, 155 + 480, 0.05],
                 [155 + 480, 260 + 480, 0],
                 [260 + 480, 275 + 480, 0.2],
                 [275 + 480, 295 + 480, 0.6],
                 [310 + 480, 160 + 720, 1]
                 ]

schedule_camping = [[0, 100, 1.0],
                    [100, 170, 0.8],
                    [170, 240, 0.1],
                    [240, 260, 0.2],
                    [260, 295, 0.6],
                    [295, 240 + 110, 1.0],
                    [110 + 240, 170 + 240, 0.7],
                    [170 + 240, 240 + 240, 0.1],
                    [240 + 240, 300 + 240, 0.8],
                    [300 + 240, 480 + 110, 1.0],
                    [110 + 480, 170 + 480, 0.7],
                    [170 + 480, 240 + 480, 0.1],
                    [240 + 480, 270 + 480, 0.2],
                    [270 + 480, 310 + 480, 0.5],
                    [310 + 480, 160 + 720, 1.0]
                    ]




# Initializing simulation
t0 = time.time()
sql_lock = threading.Lock()

stages = [Stage('Negrita Stage', artists_schedule_negrita),
          Stage('Jager Stage', artists_schedule_jager),
          Stage('Aguila Stage', artists_schedule_aguila)]

areas = [Zone('WC', 0.3, schedule_wc),
         Zone('Food Truck 1', 0.5, schedule_food_truck),
         Zone('Food Truck 2', 0.5, schedule_food_truck)]

campings = [Zone('Home', 1, schedule_home),
            Zone('Camping', 7.5, schedule_camping),
            Zone('Glamping', 7.5, schedule_camping)]

checkin = Checkin()

festival = Festival(stages=stages, areas=areas, campings=campings, checkin=checkin)


attendees = [Attendee(id=i,camping=0,festival=festival) for i in range(0,40)] +\
            [Attendee(id=i,camping=1,festival=festival) for i in range(40,80)] + \
            [Attendee(id=i,camping=2,festival=festival) for i in range(80,100)]



elements =  attendees+  [checkin] + areas+ campings  +stages


def thread_function(element):
    element.run()


threads = []
for element in elements:
    thread = threading.Thread(target=thread_function,args=(element,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()