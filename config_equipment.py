# ============================================
# Pharmaceutical Factory Energy Consumption Analysis System - Equipment and Energy Mapping Configuration
# ============================================

equip_dic = {
    'elec31': 'Equipment in the explosion-proof rooms', 'elec30': 'Air conditioning fan power distribution',
    'elec3': 'Public system fire protection', 'elec4': 'Public power supply06A1',
    'elec68': 'ice maker1 ZHLX1', 'elec69': 'ice maker2 ZHLX2',
    'elec67': 'CIP station equipment', 'elec50': 'outsourcing section of the powder production line',
    'elec43': 'Granule packaging line', 'elec38': 'main distribution panel 3A1',
    'elec32': '3A4 left main meter', 'elec33': '3A4 right main meter',
    'elec34': '3A3 left main meter', 'elec35': '3A3 right main meter',
    'elec36': '3A2 left main meter', 'elec37': '3A2 right main meter',
    'elec41': 'Bottled product line X3073-1', 'elec42': 'Bottled product line X3073-2',
    'elec46': 'Integrated washing and drying bottle machine', 'elec39': 'Middle sealing film wrapping machine',
    'elec44': 'Atlas air compressor', 'elec47': 'Jaguar air compressor',
    'elec48': 'purified water system', 'elec49': 'Improvement of the whole-grain machine',
    'elec40': 'Powder filling compartment M3081a', 'elec51': 'Powder filling compartment M3081b',
    'elec52': 'tablet press M3035', 'elec53': 'tablet press M3037',
    'elec19': 'Raw material and auxiliary material feeding area', 'elec54': 'Capsule Filling Machine',
    'elec55': 'Aluminum-plastic packaging line', 'elec58': 'lighting distribution box',
    'elec56': 'Socket distribution box 3LX1', 'elec57': 'Socket distribution box 3LX2',
    'elec59': 'fluid bed granulator D2021a', 'elec60': 'fluid bed granulator D2021b',
    'elec61': 'coating machine M3041a', 'elec62': 'coating machine M3041b',
    'elec65': 'cooling tower fan 1ZKTX1', 'elec64': 'Cleanroom equipment, air conditioning',
    'water110': 'Municipal administrator', 'water120': 'Fire water tank 1', 'water122': 'Fire water tank 2',
    'water100': 'High-pressure water supply in the preparation workshop', 'water101': 'Low-pressure water supply in the preparation workshop',
    'water105': 'First floor of the extraction workshop 1', 'water102': 'The fourth floor laboratory of the extraction workshop 1',
    'water103': 'First floor of the extraction workshop 2', 'water117': 'The first floor of the boiler room',
    'water115': 'The first floor of the engineering building', 'water116': 'The first floor of the Chinese medicinal materials warehouse',
    'water114': 'Greening water for the comprehensive use buildings', 'water156': 'Integrated building wastewater treatment',
    'water111': 'herbal decoction workshop', 'water112': 'Sewage regulating tank and circulating water tank',
    'water113': 'Class A reservoir of the sewage regulating tank', 'steam143': 'Boiler room steam',
    'steam142': 'Total steam in the preparation workshop', 'steam140': 'High-pressure steam in the preparation workshop',
    'steam141': 'low-pressure steam in the preparation workshop', 'gas2': 'Gas main pipeline metering',
    'gas3': 'Gas main metering system'
}

# public equipment
utility_system = [
    "elec30", "elec3", "elec4", "elec68", "elec69", "elec44",
    "elec47", "elec48", "elec58", "elec56", "elec57", "elec65", "elec64"
]

# workshop appliance
equipments = [
    "elec31", "elec67", "elec50", "elec43", "elec41", "elec42",
    "elec46", "elec39", "elec49", "elec40", "elec51",
    "elec52", "elec53", "elec19", "elec54", "elec55",
    "elec59", "elec60", "elec61", "elec62"
]
