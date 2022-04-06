class metric_calculations:
    
    def calculate_accuracy(tn, tp, n):
        if (tn<0 or tp<0 or n <= 0 or (int(tp) + int(tn)>n)):
            print('Invalid parameters passed to calculate accuracy')
            return 0
        accuracy = (int(tn)+int(tp))/int(n)
        return accuracy

    def calculate_precision(tp, fp):
        if (fp<0 or tp<0):
            print('Invalid parameters passed to calculate precision')
            return 0
        precision = tp/(tp+fp)
        return precision

    def calulate_recall(tp, fn):
        if (fn<0 or tp<0):
            print('Invalid parameters passed to calculate recall')
            return 0
        recall = tp/(tp+fn)
        return recall


    def calculate_f1(precision, recall):
        if ((precision < 0) or (precision > 1) or ((recall < 0) or (recall > 1))):
            print('Invalid parameters passed to calculate f1')
            return 0
        f1 = (2*(recall*precision))/(precision+recall)
        return f1