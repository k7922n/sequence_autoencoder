import ast
import cPickle
import string

def read_corpus():
	corpus   = open('../corpus/cornell_movie-dialogs_corpus/movie_conversations.txt')
	subtitle = open('../corpus/cornell_movie-dialogs_corpus/movie_lines.txt')
	sublist = {}

	for line in subtitle.readlines():
		split = line.split(' +++$+++ ')
		sublist[split[0]] = split[4]

	total_subtitle = []
	for line in corpus.readlines():
		split = line.split(' +++$+++ ')[3]
		split = ast.literal_eval(split)
		conversation = []
		for i in split:
			conversation.append(sublist[i])
		total_subtitle.append(conversation)
	f = open('subtitle.save', 'wb')
	cPickle.dump(total_subtitle, f, protocol = cPickle.HIGHEST_PROTOCOL)
	return total_subtitle

def load_corpus():
	f = open('subtitle.save', 'rb')
	load_sub = cPickle.load(f)
	return load_sub

def build_lexicon(read):
	# read(bool) means read form saves file or not 
	if read:
		subs = read_corpus()
	else:
		subs = load_corpus()
	# create dict and list
	index2word = []
	word2index = {}
	for sub in subs:
		for item in sub:
			item = item.translate(None, string.punctuation).split()
			for i in item:
				print i
	#TODO

def form_txt():
	sub = load_corpus()
	source = open('source.txt', 'w')
	target = open('target.txt', 'w')
	dev_source = open('dev_source', 'w')
	dev_target = open('dev_target', 'w')
	
	for s, turns in enumerate(sub):
		for i in range(len(turns) - 1):
			'''
			if s >= 82900:
				dev_source.write(turns[i])
				dev_target.write(turns[i + 1])
				break
			'''
			source.write(turns[i])
			target.write(turns[i + 1])
	source.close()
	target.close()
	dev_source.close()
	dev_target.close()
	
def form_neural_comversation_txt():
	sub = load_corpus()
	train = open('Cornell_train.csv', 'w')
	valid = open('Cornell_valid.csv', 'w')	

	for s, turns in enumerate(sub):
		for i in range(len(turns) - 1):
			if s > 82900:
				valid.write(turns[i].translate(None, '\n') + '\t' + turns[i+1])
				break
			train.write(turns[i].translate(None, '\n') + '\t' + turns[i+1])
	train.close()
	valid.close()
			
if __name__ == '__main__':
	form_txt()
