import re # za regularni izraz 
import codecs
try :
    anotated_tweets_file = open('corpus_anotated_tweets.txt','r')
except:
    anotated_tweets_file = open('corpus_anotated_tweets.txt','w+')
anotated_tweets = [x.split(' - ')[1] for x in anotated_tweets_file]
anotated_tweets_file.close()

print 'Broj anotacija: %d' % len(anotated_tweets)

start_line_index = 100 # Od koje linije se cita korpus
if start_line_index > 1000000:
    print 'Upisao si broj veci od milijun, pricekaj malo...'

#corpus = open('hrsrTweets.txt', 'r')
corpus = codecs.open( "hrsrTweets.txt", "r", "utf-8" )
fresh_annotations = []
quoted = re.compile('"[^"]*"')
text_phase = False #reading phase of tweet text lines
tweets_properly_started = False #if the chosen line is in the middle of a tweet
j = 0
i = 0
lines = []
for line in corpus:
    j += 1
    if i >= start_line_index:
        if not tweets_properly_started and '<tweet' not in line:
            continue            
        if '<tweet' in line:
            tweets_properly_started = True
            tweet_id = quoted.findall(line)[0][1:-1]  
            if tweet_id in anotated_tweets:
                continue
        elif '<text>' in line:
            if tweet_id in anotated_tweets:
                continue
            lines = [line]
            if '</text>' not in line:
                text_phase = True
        elif text_phase:
            if tweet_id in anotated_tweets:
                continue
            lines.append(line)
            if '</text>' in line:
                text_phase = False
        if len(lines) and not text_phase:
            if tweet_id in anotated_tweets:
                continue
            tweet_text = ''.join(lines)[6:-8]
            lines = []
            print '------------------------'
            print 'Linija u korpusu: %d' % j
            print 'ID: %s\n' % tweet_id
            print tweet_text
            print '------------------------'
            try:
                category = raw_input('Category? ')
                if '#' in category:
                    start_line_index += int(category[1:])
                    continue
                category = int(category)
                print ""
                if category < 0: break
                fresh_annotations.append((j,tweet_id,category))
            except:
                break
    i += 1
anotated_tweets_file = open('corpus_anotated_tweets.txt','a+')
for (j, tweet_id, tweet_category) in fresh_annotations:
    anotated_tweets_file.write('%d - %s - %d\n' % (j, tweet_id,tweet_category))
    anotated_tweets.append(tweet_id)
anotated_tweets_file.close()
corpus.close()
    
    
print 'Ukupno novih anotacija: %d' % len(fresh_annotations)
