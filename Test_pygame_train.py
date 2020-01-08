import pygame_sim as env 
import random
import numpy as np
import tensorflow
from collections import deque
from tensorflow.keras.models     import Sequential
from tensorflow.keras.layers     import Dense
from tensorflow.keras.optimizers import Adam
import time

class DQNAgent:
	def __init__(self, state_size, action_size):
		self.state_size = state_size
		self.action_size = action_size
		self.memory = deque(maxlen=2000)
		self.gamma = 0.95    # discount rate
		self.epsilon = 1.0  # exploration rate
		self.epsilon_min = 0.1
		self.epsilon_decay = 0.92
		self.learning_rate = 0.001
		self.model = self._build_model()
		self.high_score = 0

	def _build_model(self):
		# Neural Net for Deep-Q learning Model
		model = Sequential()
		model.add(Dense(24, input_dim=self.state_size, activation='relu'))
		model.add(Dense(24, activation='relu'))
		model.add(Dense(self.action_size, activation='linear'))
		model.compile(loss='mse',
					  optimizer=Adam(lr=self.learning_rate))
		return model

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done))

	def act(self, state, test):
		if np.random.rand() <= self.epsilon and test == False:
			return random.randrange(self.action_size)
		act_values = self.model.predict(state)
		return np.argmax(act_values[0])  # returns action

	def replay(self, batch_size):
		minibatch = random.sample(self.memory, batch_size)
		for state, action, reward, next_state, done in minibatch:
			#print("s,a,r,ns,d: ",state,action,reward,next_state,done)
			target = reward
			if not done:
				target = (reward + self.gamma *
						  np.amax(self.model.predict(next_state)[0]))
			#print("Predict1")
			target_f = self.model.predict(state)
			#print("Predict2")
			#print(target)
			target_f[0][action] = target
			#print(target_f)
			#print("Predict3")
			self.model.fit(state, target_f, epochs=6, verbose=0)
		#print("out of for loop")
		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay

	def load(self, name):
		self.model.load_weights(name)

	def save(self, name):
		self.model.save_weights(name)

	def high_score_checker(self, new_score):
		if new_score > self.high_score:
			self.high_score = new_score
			return True
		return False


# run through training loop
def train_sequence(agent, remember, easy_mode):
	#reinit score to 0 for each game
	score = 0

	state = env.reset(background, car_pic, SCREEN)
	#print("State: ",state)
	state = np.reshape(state, [1, state_size])

	if remember:
		display = False
	else:
		display = True

	print("\n") # to allow our /r to work down in the for loop properly
	for time in range(2000):
		action = agent.act(state,display)
		next_state, reward, done, _ = env.step(action, display, SCREEN, car_pic, car, background, easy_mode)
		reward = reward if not done else -10
		score += reward

		if reward < 0 and display:
			print("Collision    ", end="\r")
		elif display:
			print("No Collision ", end="\r")

		if done:
			break
		#print("R: ", reward, "S: ", score, "ST: ", next_state)

		next_state = np.reshape(next_state, [1, state_size])
		
		if remember:
			agent.remember(state, action, reward, next_state, done)
		
		state = next_state
		#print("State:Done", state, done)
	if done != True:
		return 1337
	else:
		return score


# retrieve the highest score from all of the agents in play
def get_high_score(agents):
	highscore = 0
	for a in agents:
		if a.high_score > highscore:
			highscore = a.high_score
	return highscore



# Test the current iteration of the model, if its better than the last save, else nah
def test_model(agents, easy_mode):
	old_high_score = get_high_score(agents)
	new_high_score = old_high_score
	best_agent = DQNAgent(state_size, action_size)
	
	counter = 0

	for agent in agents:
		#reinit score to 0 for each game
		score = 0
		counter+=1
		score = train_sequence(agent, False, easy_mode)

		print("\n\n   Score for agent {}: {}".format(counter, score))

		#if the new score for the agent is higher than its last, and if the score is higher than any other sccofe posted that is higher than that agents last

		if (agent.high_score_checker(score)):
			if score > new_high_score:
				new_high_score = score
				best_agent = agent

	"""
	try:
		agent.load("car_avoid-dqn.h5")
		score = train_sequence(agent, False, easy_mode)
		print("    Score for prev best model: {}\n\n".format(score))

	except Exception as e:
		print(e)
		print("You likely didnt have a car_avoid-dqn.h5 already there, i need to fix that")
	"""
	
	if score > new_high_score:
		new_high_score = score
		best_agent = agent
		best_agent.high_score = score


	#Determining best model
	if ( new_high_score > old_high_score ):
		print("\n\nHigh score: {}|| Old: {}\n\n".format(new_high_score, old_high_score))
		best_agent.save("car_avoid-dqn.h5")

	else:
		print("Score to beat: ", old_high_score)


EPISODES = 5000

if __name__ == "__main__":
	pygame, SCREEN, car_pic, background, running, car = env.init()
	state_size = 7#env.observation_space.shape[0]
	action_size = 4#env.action_space.n

	"""
		Lets make this thing run more of a batch generational approach
	"""
	agent0 = DQNAgent(state_size, action_size) # this is another free agent who can do whatever it wants
	agent1 = DQNAgent(state_size, action_size) # last agent in list will be used to store prev best
	
	#agent2 = DQNAgent(state_size, action_size) 
	#agent3 = DQNAgent(state_size, action_size)
	#agent4 = DQNAgent(state_size, action_size)

	agents = [agent0,agent1]#, agent1, agent2, agent3, agent4]
	#test = True
	#agent.load("car_avoid-dqn.h5")

	test = False
	easy_mode = True  # this is the easiest learning mode for it, boxes spawn directly on top of the car
	done = False
	batch_size = 100

	for e in range(EPISODES):

		if e > 15:
			easy_mode = False

		if e % 15 == 0:
			test_model(agents, easy_mode)
			try:
				agents[1].load("car_avoid-dqn.h5") # last one is placeholder for prev best

			except Exception as ex:
				print(ex)

		

		agent_counter = 0
		for agent in agents:     
			score = train_sequence(agent, True, easy_mode)
				
			if score == 1337:
				easy_mode = False

			print("Episode: {}:{}, Epsilon: {}, Score: {}".format(e, EPISODES, agent.epsilon, score))
			agent_counter+=1
			if len(agent.memory) > batch_size:
				#print("Replay")
				try:
					agent.replay(batch_size)
				except Exception as e:
					print(e)
			if agent_counter >= len(agents)-1: # last agent in our list is prev best, dont train him
				break