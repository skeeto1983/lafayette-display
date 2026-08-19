import time

from app.services.vu import VUService


vu = VUService()
vu.start()

try:
    for _ in range(20):
        print(vu.get_levels())
        time.sleep(0.1)

finally:
    vu.stop()
