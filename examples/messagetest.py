import multiprocessing
import time

def processor(e):
    """Wait for the event to be set before doing anything"""
    print('processor doing the stuff')
    time.sleep(5)
    print ('processor notifying is done')
    e.set()

def renderer(e):
    """Wait t seconds and then timeout"""
    print('renderer waiting for the stuff')
    e.wait()
    print('renderer notiffied e.is_set()-> {}'.format(e.is_set()))


if __name__ == '__main__':
    e = multiprocessing.Event()
    w1 = multiprocessing.Process(name='block', 
                                 target=processor,
                                 args=(e,))

    w2 = multiprocessing.Process(name='non-block', 
                                 target=renderer, 
                                 args=(e,))

    w1.start()
    w2.start()

    print('thread finish')