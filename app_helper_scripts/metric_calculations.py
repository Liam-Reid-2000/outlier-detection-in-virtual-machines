class metric_calculations:
    def calculate_accuracy(tn, tp, n):
        accuracy = 0
        try:
            accuracy = (int(tn)+int(tp))/int(n)
        except:
            accuracy = 0
            print('acc acuracy = ' + accuracy)
        return accuracy


    def calculate_precision(tp, fp):
        precision = 0
        try:
            precision = tp/(tp+fp)
        except:
            precision = 0
        return precision


    def calulate_recall(tp, fn):
        recall = 0
        try:
            recall = tp/(tp+fn)
        except:
            recall = 0
        return recall


    def calculate_f1(precision, recall):
        f1 = 0
        try:
            f1 = (2*(recall*precision))/(precision+recall)
        except:
            f1 = 0
        return f1