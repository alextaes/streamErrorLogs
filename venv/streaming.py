
import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

if __name__ == "__main__":
    sc = SparkContext(appName="StreamingErrorCount")
    ssc = StreamingContext(sc, 2)
    ssc.checkpoint("file:///tmp/spark")

    lines = ssc.socketTextStream(sys.argv[1], int(sys.argv[2]))

    def countWords(newValues, lastSum):
        if lastSum is None:
            lastSum = 0
        return sum(newValues, lastSum)

    word_counts = lines.flatMap(lambda line: line.split(" "))\
                       .filter(lambda word: "ERROR" in word)\
                       .map(lambda word: (word, 1))\
                       .reduceByKeyAndWindow(lambda a, b: a + b,
                                             lambda a, b: a - b, #substract opp when the tuples move out of the window
                                             20, 2)
                       #.updateStateByKey(countWords)
    word_counts.pprint()
    ssc.start()
    ssc.awaitTermination()
