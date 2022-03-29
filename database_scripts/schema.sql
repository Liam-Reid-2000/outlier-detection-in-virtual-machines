CREATE TABLE detection(
    detection_id int primary key,
    detector_name text,
    dataset_name text,
    fn_count int,
    accuracy float,
    precision float,
    recall float,
    f1 float
);

CREATE TABLE true_positives(
    tp_pk int primary key,
    detection_id int,
    true_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_positives(
    tp_pk int primary key,
    detection_id int,
    false_positive_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);

CREATE TABLE false_negatives(
    tp_pk int primary key,
    detection_id int,
    false_negative_datetime datetime,
    FOREIGN KEY(detection_id) REFERENCES detection(detection_id)
);
