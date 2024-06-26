import gpiozero
import asyncio


def led_init():
    try:
        state_led = gpiozero.LED(17)
        auth_led = gpiozero.LED(27)
        state_led.on()
        auth_led.off()
    except gpiozero.BadPinFactory as e:
        state_led = None
        auth_led = None
        print(e)

    return state_led, auth_led


async def led_blink(led, interval, count):
    if led is None:
        return
    for i in range(count):
        led.on()
        await asyncio.sleep(interval)
        led.off()
        await asyncio.sleep(interval)
