from HelperModule.timer import Timer
from typing import Dict, List, Tuple


class SRWindow:

    def __init__(self, limit: int):
        self._dictionary: Dict[int, Tuple[bytes, Timer]]= {}
        self._limit = limit
        self._packet_count = 0

    def release(self, ack_num: int) -> bool:
        if ack_num in self._dictionary:
            del self._dictionary[ack_num]
            self._packet_count -= 1
            return True
        return False

    def append(self, seq_num: int, packet: bytes, timer: Timer):
        if self._packet_count is self._limit:
            return False
        self._dictionary[seq_num] = (packet, timer)
        self._limit += 1
        return True
    
    def __len__(self):
        return self._packet_count

    def check_timers(self) -> List[int]:
        expired_seq_nums = []
        for k in self._dictionary:
            running = self._dictionary[k][1].timeout()
            if not running:
                expired_seq_nums.append(k) 
        return expired_seq_nums
    
    def restart_timer(self, seq_num):
        timer = self._dictionary[seq_num][1]
        timer.stop()
        timer.start()
        
    def get_seq_nums(self):
        return list(self._dictionary.keys()).sort()

    def pop_and_slide(self, number_of_iterations: int = 1) -> int:
        keys = self.get_seq_nums()
        for i in range(number_of_iterations):
            self.release(keys[i])
        return self._limit - self.__len__()