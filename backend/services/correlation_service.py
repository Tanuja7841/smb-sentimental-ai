from collections import Counter


incident_memory = []


def track_incident(incident_type):

    incident_memory.append(incident_type)


def detect_pattern():

    counter = Counter(incident_memory)

    return counter.most_common(3)