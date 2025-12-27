from abc import ABC, abstractmethod
from enum import Enum
import uuid
from collections import defaultdict

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    
class SignalTiming:
    def __init__(self, green:int,red:int,yellow:int):
        self.green = green
        self.red = red
        self.yellow = yellow
        
class SignalState(ABC):
    
    @abstractmethod
    def action(self,signal:"TrafficSignal"):
        pass
    
class RedState(SignalState):
    
    def action(self, signal:"TrafficSignal"):
        print(f"[{signal.direction.value}] RED")
        print(f"{signal.timing.red}s")
        signal.set_state(signal.green_state)
        
class GreenState(SignalState):
    
    def action(self, signal:"TrafficSignal"):
        print(f"[{signal.direction.value}] Green")
        print(f"{signal.timing.green}s")
        signal.set_state(signal.yellow_state)
        
class YellowState(SignalState):
    
    def action(self, signal:"TrafficSignal"):
        print(f"[{signal.direction.value}] Yellow")
        print(f"{signal.timing.yellow}s")
        signal.set_state(signal.green_state)
        
class TrafficSignal:
    def __init__(self,direction:Direction, timing:SignalTiming):
        self.id = str(uuid.uuid4())
        self.direction = direction
        self.timing = timing
        self.curr_green_timing = timing.green
        self.curr_state = RedState()
        self.red_state = RedState()
        self.green_state = GreenState()
        self.yellow_state = YellowState()
        
    def set_state(self, state:SignalState):
        self.curr_state = state
        
    def change(self):
        self.curr_state.action(self)
        
class Intersection:
    def __init__(self,directions:list[Direction],timing:SignalTiming):
        self.id = str(uuid.uuid4())
        self.signals: dict[Direction,TrafficSignal] = {
            d:TrafficSignal(d,timing) for d in directions
        }
        self.directions = directions
        self.curr_idx = 0

class IntersectionRepo(ABC):
    @abstractmethod
    def save(self,intersection:Intersection):
        pass
    
    @abstractmethod
    def get(self,i_id:str):
        pass
    
    @abstractmethod
    def get_all(self):
        pass
    
class TrafficSignalRepository(ABC):
    
    @abstractmethod
    def get_all(self):
        pass
    
class VehicleCountRepo(ABC):
    
    @abstractmethod
    def increment(self,intersection:Intersection,direction:Direction,count:int)->None:
        pass
    
    @abstractmethod
    def get(self,i_id:str,direction:Direction):
        pass
    
class EmergencyRepo(ABC):
    
    @abstractmethod
    def set(self,i_id:str, direction:Direction):
        pass
    
    @abstractmethod
    def clear(self,i_id:str):
        pass
    
    @abstractmethod
    def get(self,i_id:str):
        pass
    
class InMemoryIntersectionRepo(IntersectionRepo):
    def __init__(self):
        self._data:dict[str,Intersection] = defaultdict(lambda:None)
        
    def save(self,intersection:Intersection):
        self._data[intersection.id] = intersection
        
    def get(self,i_id:str):
        return self._data[i_id]
        
    def get_all(self):
        return list(self._data.values())
        

    
class InMemoryTrafficSignalRepository(TrafficSignalRepository):
    
    def get_all(self,intersection:Intersection):
        return list(intersection.signals.values())
     

class InMemoryVehicleCountRepo(VehicleCountRepo):
    def __init__(self):
        self._data:dict[str,dict[Direction,int]] = defaultdict(lambda:int)
        
    def increment(self,intersection_id:str,direction:Direction,count:int):
        self._data[intersection_id][direction] += count
        
    def get(self,i_id:str,direction:Direction):
        return self._data[i_id][direction]
        
class InMemoryEmergencyRepo(EmergencyRepo):
    def __init__(self):
        self._data:dict[str,Direction] = defaultdict(lambda:None)
        
    def set(self,i_id:str,dirction:Direction):
        self._data[i_id] = direction
        
    def clear(self,i_id:str):
        self._data[i_id] = None
        
    def get(self,i_id:str):
        return self._data[i_id]

class SignalService:
    def __init__(self,repo:InMemoryTrafficSignalRepository):
        self.signal_repo = repo
        
    def set_all_red(self,intersection:Intersection):
        for signal in self.signal_repo.get_all(intersection):
            signal.set_state(signal.red_state)
            
    def activate_green(self,intersection:Intersection,direction:Direction):
        self.set_all_red(intersection)
        intersection.signals[direction].set_state(intersection.signals[direction].gree_state)

class TrafficService:
    def __init__(self, repo:VehicleCountRepo):
        self.vehicle_count_repo = repo
        
    def update_vehicle_count(self,i_id:str,direction:Direction,count:int):
        self.vehicle_count_repo.increment(i_id,direction,count)
        
    def adjust_green(self, base:int, i_id:str, direction:Direction):
        self.vehicles = self.vehicle_count_repo(i_id, direction)
        if vehicles > 20:
            return min(base + 10, 90)
        if vehicles < 5:
            return max(base - 5, 15)

class EmergencyService:
    def __init__(self, repo:EmergencyRepo,signal_service:SignalService):
        self.repo = repo
        self.signal_service = signal_service
        
    def trigger(self,i_id:str, direction:Direction):
        self.repo.set(i_id,direction)
        
    def process(self, intersection:Intersection):
        direction = self.repo.get(intersection.id)
        if not direction:
            return
        self.signal_service.activate_green(intersection,direction)
        time.sleep(10)
        self.repo.clear(intersection.id)

            
class CycleService:
    def __init__(self,i_repo:IntersectionRepo,signal_service:SignalService,emergency_service:EmergencyService,traffic_service:TrafficService,emergency_repo:EmergencyRepo):
        self.i_repo = i_repo
        self.signal_service = signal_service
        self.emergency_repo = emergency_repo
        self.traffic_service = traffic_service
        self.emergency_service = emergency_service
    
    def run(self, i_id):
        intersection = i_repo.get(i_id)
        while True:
            if self.emergency_repo.get(i_id):
                self.emergency_service.process(intersection)
                continue
            
            direction = intersection.directions[intersection.curr_idx]
            signal = intersection.signals[direction]
            signal.curr_green_timing = self.traffic_service.adjust_green(signal.timing.green,intersection.id, direction)
            self.signal_service.activate_green(intersection,direction)
            signal.change()
            signal.change()
            signal.change()
            intersection.curr_idx = (intersection.curr_idx + 1)% len(intersection.directions)
            
class TrafficController:
    def __init__(self,cycle_service:CycleService,traffic_service:TrafficService,emergency_service:EmergencyService,intersection_id:str):
        self.cycle_service = cycle_service
        self.traffic_service = traffic_service
        self.emergency_service = emergency_service
        self.intersection_id = intersection_id
        
    def start(self):
        self.cycle_service.run(self.intersection_id)
        
    def update_vehicle_count(self, direction:Direction, count:int):
        self.traffic_service.update_vehicle_count(self.intersection_id,direction, count)
        
    def emergency_request(self, direction:Direction):
        self.emergency_service.trigger(self.intersection_id,direction)

        
