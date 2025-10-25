def get_hand_landmarks(hand):
    """Extract landmarks once to avoid redundant processing"""
    return [(p.x, p.y, p.z) for p in hand.landmark]

def rock(landmarks):
    index_tip, middle_tip, ring_tip, pinky_tip = landmarks[8], landmarks[12], landmarks[16], landmarks[20]
    index_base, middle_base, ring_base, pinky_base = landmarks[5], landmarks[9], landmarks[13], landmarks[17]
    
    all_contracted = (
        index_tip[1] > index_base[1] and
        middle_tip[1] > middle_base[1] and
        ring_tip[1] > ring_base[1] and
        pinky_tip[1] > pinky_base[1]
    )
    return all_contracted

def paper(landmarks):
    thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip = landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]
    thumb_base, index_base, middle_base, ring_base, pinky_base = landmarks[2], landmarks[5], landmarks[9], landmarks[13], landmarks[17]
    
    all_extended = (
        thumb_tip[1] < thumb_base[1] and
        index_tip[1] < index_base[1] and
        middle_tip[1] < middle_base[1] and
        ring_tip[1] < ring_base[1] and
        pinky_tip[1] < pinky_base[1]
    )
    return all_extended

def scissors(landmarks):
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Check ring and pinky are curled
    ring_base = landmarks[13]
    pinky_base = landmarks[17]
    
    # Index and middle extended and separated
    distance = ((index_tip[0] - middle_tip[0])**2 + (index_tip[1] - middle_tip[1])**2)**0.5
    
    fingers_separated = distance > 0.1
    other_fingers_curled = ring_tip[1] > ring_base[1] and pinky_tip[1] > pinky_base[1]
    
    return fingers_separated and other_fingers_curled

def o_sign(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Check distance between thumb and index
    distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
    
    # Check that other fingers are extended (not a rock)
    middle_base = landmarks[9]
    ring_base = landmarks[13]
    pinky_base = landmarks[17]
    
    other_fingers_extended = (
        middle_tip[1] < middle_base[1] and
        ring_tip[1] < ring_base[1] and
        pinky_tip[1] < pinky_base[1]
    )
    
    if distance < 0.07 and other_fingers_extended:
        x = (thumb_tip[0] + index_tip[0]) / 2
        y = (thumb_tip[1] + index_tip[1]) / 2
        return True, x, y
    return False, None, None