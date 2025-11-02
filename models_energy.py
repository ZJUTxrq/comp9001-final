from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Energy:
    timestamp: datetime
    elec31: Optional[float] = None
    elec30: Optional[float] = None
    elec3: Optional[float] = None
    elec4: Optional[float] = None
    elec68: Optional[float] = None
    elec69: Optional[float] = None
    elec67: Optional[float] = None
    elec50: Optional[float] = None
    elec43: Optional[float] = None
    elec38: Optional[float] = None
    elec32: Optional[float] = None
    elec33: Optional[float] = None
    elec34: Optional[float] = None
    elec35: Optional[float] = None
    elec36: Optional[float] = None
    elec37: Optional[float] = None
    elec41: Optional[float] = None
    elec42: Optional[float] = None
    elec46: Optional[float] = None
    elec39: Optional[float] = None
    elec44: Optional[float] = None
    elec47: Optional[float] = None
    elec48: Optional[float] = None
    elec49: Optional[float] = None
    elec40: Optional[float] = None
    elec51: Optional[float] = None
    elec52: Optional[float] = None
    elec53: Optional[float] = None
    elec19: Optional[float] = None
    elec54: Optional[float] = None
    elec55: Optional[float] = None
    elec58: Optional[float] = None
    elec56: Optional[float] = None
    elec57: Optional[float] = None
    elec59: Optional[float] = None
    elec60: Optional[float] = None
    elec61: Optional[float] = None
    elec62: Optional[float] = None
    elec65: Optional[float] = None
    elec64: Optional[float] = None
    water110: Optional[float] = None
    water120: Optional[float] = None
    water122: Optional[float] = None
    water100: Optional[float] = None
    water101: Optional[float] = None
    water105: Optional[float] = None
    water102: Optional[float] = None
    water103: Optional[float] = None
    water117: Optional[float] = None
    water115: Optional[float] = None
    water116: Optional[float] = None
    water114: Optional[float] = None
    water156: Optional[float] = None
    water111: Optional[float] = None
    water112: Optional[float] = None
    water113: Optional[float] = None
    steam143: Optional[float] = None
    steam142: Optional[float] = None
    steam140: Optional[float] = None
    steam141: Optional[float] = None
    gas2: Optional[float] = None
    gas3: Optional[float] = None


@dataclass
class Process:
    process_id: int = field(default=0)
    process_date: datetime = field(default_factory=datetime.now)
    product_type: str = ""        # product
    process_name: str = ""        # process name
    size: str = ""                # size
    number: int = 0               # batch number
    investnumber: float = 0.0     # input
    worker_number: int = 1        # number of positions
    pronumber: float = 0.0        # production quantity
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    equipments: str = ""          # equipment name
    process_time: float = 0.0     # Duration (hours)
    optimize_start_time: Optional[datetime] = None
    optimize_end_time: Optional[datetime] = None

    def calc_duration(self):
        self.process_time = (self.end_time - self.start_time).total_seconds() / 3600
        return self.process_time

    def set_optimized_time(self, start: datetime, end: datetime):
        self.optimize_start_time = start
        self.optimize_end_time = end

