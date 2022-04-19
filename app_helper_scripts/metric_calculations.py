from app_helper_scripts.app_exceptions import InvalidPercentageFloatValueError, InvalidValueForCalculationError

class metric_calculations:
    """Calcaultes evaluation metrics based on confusion matrix data"""
    
    def calculate_accuracy(tn, tp, n):
        if (tn<0 or tp<0 or n <= 0 or (int(tp) + int(tn)>n)):
            raise InvalidValueForCalculationError([tn,tp,n])
        accuracy = (int(tn)+int(tp))/int(n)
        return accuracy

    def calculate_precision(tp, fp):
        if (fp<0 or tp<0 or fp+tp==0):
            raise InvalidValueForCalculationError([fp,tp])
        precision = tp/(tp+fp)
        return precision

    def calulate_recall(tp, fn):
        if (fn<0 or tp<0 or fn+tp==0):
            raise InvalidValueForCalculationError([fn,tp])
        recall = tp/(tp+fn)
        return recall

    def calculate_f1(precision, recall):
        if (precision+recall == 0):
            raise InvalidValueForCalculationError([precision,recall])
        if ((precision < 0 or precision > 1) or (recall < 0 or recall > 1)):
            raise InvalidPercentageFloatValueError([precision, recall])
        f1 = (2*(recall*precision))/(precision+recall)
        return f1