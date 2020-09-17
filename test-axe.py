import gym
import minerl


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    name = 'ChestClockNoisy{}-v0'.format(0)
    env = gym.make(name)
    for __ in range(5):
        print("NEW EPISODE")
        state = env.reset()
        for _ in range(10000):
            env.step(env.action_space.sample())