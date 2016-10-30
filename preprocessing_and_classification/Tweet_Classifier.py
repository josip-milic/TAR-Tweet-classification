# -*- coding: utf-8 -*-
import pickle, re, os
import numpy as np
from subprocess import call, Popen, PIPE
from scipy.sparse import csr_matrix
import sys



intermediate_dir = 'intermediate/'

tweet_categories = {}
tweet_categories[1] = 'PRIVATE'
tweet_categories[2] = 'DEALS'
tweet_categories[3] = 'NEWS_TECHNOLOGY'
tweet_categories[4] = 'NEWS_POLITICS'
tweet_categories[5] = 'NEWS_SPORT'
tweet_categories[6] = 'NEWS_REST'
tweet_categories[7] = 'REST'

enhance_sets = {}
enhance_sets[1] = set() # (PRIVATE) not used 
enhance_sets[2] = set(['posao','prodaja','stan','automobil','oglasnikpopusti','php','java','css','html','dev','androiddev','mysql','linux','c','programer','javite','sysadmin','developere','natječaj','konobar'])
enhance_sets[3] = set(['seum','uber', 'airbnb','google','amazon','apple','haker','digitalan','gfxbench','mwc','samsung','gaming','twitter'])
enhance_sets[4] = set(['udruga','franak','uhljeb','komisija','đukanović','jokić','šustar','banka'])
enhance_sets[5] = set(['doping','uefacom','ademi','moo','čačić','euro','nogomet'])
enhance_sets[6] = set(['naoblaka','vrijeme','sunčan','sunčano','naoblak','lokalan','pljusak','grmljavina','pretežno','pretežan','toplo'])
enhance_sets[7] = set(['poveznica'])

def enhance_vectors(list_of_data, tfidf_vectors_of_data, print_progress = True):
    enhanced_vectors = tfidf_vectors_of_data.copy()
    enhanced_vectors._shape = (tfidf_vectors_of_data.shape[0],tfidf_vectors_of_data.shape[1]+6)
    indptr = enhanced_vectors.indptr
    data = enhanced_vectors.data
    indices = enhanced_vectors.indices
    
    
    for i in range(tfidf_vectors_of_data.shape[0]):
        words = set(list_of_data[i].strip().split(' '))
        for ann in range(2,8):
            enhancement = len(enhance_sets[ann].intersection(words))
            data = np.insert(data,indptr[i+1],enhancement)
            indices = np.insert(indices,indptr[i+1],tfidf_vectors_of_data.shape[1]+(ann-2))
            for j in range(i+1,indptr.shape[0]):
                indptr[j] += 1
        
        if (i % 1000 == 0) and i != 0:
            if print_progress: print 'Enhanced: %d/%d vectors' % (i,tfidf_vectors_of_data.shape[0])
        
    csr_mat = csr_matrix( (data,indices,indptr), shape=enhanced_vectors.shape )
    return csr_mat

def purge(tweet_text):
    purged = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', tweet_text).strip()
    purged_spl = purged.split(' ')
    if (purged) and (purged_spl[-1][0] in '^'):
        purged = ' '.join(purged_spl[:-1]).strip()
    for forbidden in '!&.?-–^,;:"\'/[]{}()<>':
        while forbidden in purged:
            purged = purged.replace(forbidden,'')
    
    purged = purged.strip()
    if purged == '':
        return 'poveznica'
    return purged

def classify_tweet_text(tweet_text, clf, vectorizer):
    target_name = intermediate_dir + 'purged_tweet.txt'
    
    open(target_name,'w').write(purge(tweet_text)+'\n')
    command = ['"NLPToolkit.exe"','-pre', '-pos', '-lm', '"'+target_name+'"', '"'+target_name.replace('purged','pre_purged')+'"']
    #print ' '.join(command)
    p = Popen(' '.join(command), stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()    
    
    #x = call(' '.join(command),shell=True)
    f = open(target_name.replace('purged','pre_purged'),'r')
    processed_tweet_text = ''
    for line in f:
        if ( line != "\n"):
            word = line.split('\t')[2].strip().lower()
            processed_tweet_text += word+' '
        else:
            processed_tweet_text = processed_tweet_text.rstrip()
    f.close()
    os.remove(target_name)
    os.remove(target_name.replace('purged','pre_purged'))
    #print 'Original text: "%s"' % tweet_text
    #print 'Preprocessed text: "%s"' % processed_tweet_text
    #print ''
    X_tweet = enhance_vectors([processed_tweet_text],vectorizer.transform([processed_tweet_text]), print_progress = False)
    
    return tweet_categories[clf.predict(X_tweet)[0]]  
    
def classify_tweet_texts(tweet_texts, clf, vectorizer):
    return [classify_tweet_text(tweet_text, clf, vectorizer) for tweet_text in tweet_texts]

vectorizer = pickle.load( open( "saved_objects/vectorizer.pkl", "rb" ) )
clfs_dict = pickle.load( open( "saved_objects/classifiers.pkl", "rb" ) )

#clf = clfs_dict['clf_svm']
#clf = clfs_dict['clf_log_reg']
#clf = clfs_dict['clf_knn']

file_name = sys.argv[1]
clf_name = sys.argv[2]
clf = clfs_dict[clf_name]
examples = open(file_name,'r').readlines()
#examples = ['Samsung je objavio', 'Karamarko je objavio', 'Messi je objavio']
classes = classify_tweet_texts(examples,clf,vectorizer)
open(file_name.replace('.txt','_classified.txt'),'w').write('\n'.join(classes)+'\n')

