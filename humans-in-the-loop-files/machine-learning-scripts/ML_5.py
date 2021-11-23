

# Run spacy crf suite on business listings to identify the individual tokens within a business listing

from Repository import Repository
from spacy_crfsuite import read_file
import spacy

from spacy_crfsuite.tokenizer import SpacyTokenizer
from spacy_crfsuite.train import gold_example_to_crf_tokens
from spacy_crfsuite import CRFExtractor
from Repository import Repository
from Annotation import Annotation
from Coordinate import Coordinate
from DataSource import DataSource
from TextValue import TextValue
from datetime import datetime

import srsly


def main():
    print("Starting process")
    tokenizer, crf_extractor = train_nlp()
    run_nlp(tokenizer, crf_extractor)

def train_nlp():
    print("training nlp")
    repo = Repository()
    #path = create_training_data_markdown()
    path = "business_listing_training.md"
    train_data = read_file(path)

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    tokenizer = SpacyTokenizer(nlp)

    train_dataset = [
        gold_example_to_crf_tokens(ex, tokenizer=tokenizer) 
        for ex in train_data
    ]
    
    component_config = srsly.read_json("spacy_crf_config.json")

    crf_extractor = CRFExtractor(component_config=component_config)

    rs = crf_extractor.fine_tune(train_dataset, cv=5, n_iter=50, random_state=42)
    print("best_params:", rs.best_params_, ", score:", rs.best_score_)
    crf_extractor.train(train_dataset)

    classification_report = crf_extractor.eval(train_dataset)
    print(classification_report[1]) 
    # example = {"text": f.read()}
    # tokenizer.tokenize(example, attribute="text")
    # results = crf_extractor.process(example)
    # print(results)
    return tokenizer, crf_extractor

def create_training_data_markdown():
    output_path = "business_listing_training.md"
    repo = Repository()
    # Get a list of Annotations where subject_type = 'business listing entities'
    annotations = repo.get_business_listing_annotations()
    with open(output_path, "w") as mdf:
        for annotation in annotations:
            #print("Annotation ID: " + str(annotation.id))
            # Get a list of coordinates where "annotation_id" = a.id
            coordinates = repo.get_coordinates(annotation.id)
            coordinates.sort(key=lambda x: x.x, reverse=False)
            md_row = "- "
            for coordinate in coordinates:
                text_value = repo.get_text_value(coordinate.id)
                if text_value is not None:
                    md_row += "[" + text_value.value + "]" + "(" +  text_value.key.replace(" ", "_") + ") "
            mdf.write(md_row + "\r\n")
            
    return output_path


def create_entity(start, end, type, value):
    return {
        'end': end,
        'entity': type,
        'start': start,
        'value': value
    }

def get_ml_version_id():
    version = "1.0.0"
    repo = Repository()
    ml_process_id = repo.get_ml_process_id('CRF entity parsing')
    ml_version_id = repo.get_ml_version_id(ml_process_id, version)
    if ml_version_id is None:
        ml_version_id = repo.insert_ml_version( ml_process_id, version)

    return ml_version_id

def run_nlp(tokenizer, crf_extractor):
    ml_version_id = get_ml_version_id()
    repo = Repository()
    annotations = repo.get_page_ocr_annotations()
    # Get a list of annotations with Page OCR
    for annotation in annotations:
        print("Annotation: " + str(annotation.id))
        # Get a list of coordinates for that annotation
        coordinates = repo.get_coordinates(annotation.id)
        type_annotation = repo.get_group_business_type_annotation(annotation.parent_id)
        if type_annotation is not None:
            # Get Coordinates for this grouping header
            type_coordinates = repo.get_coordinates(type_annotation.id)
            if len(type_coordinates) > 0:
                type_coordinate = type_coordinates[0]
                # Get text value for this group header coordinates
                text_value = repo.get_text_value(type_coordinate.id)

        for coordinate in coordinates:
            # Get a list of text values
            text_value = repo.get_text_value(coordinate.id)
            if text_value is None:
                continue
            text = {"text": text_value.value.replace("--", " ")}
            tokenizer.tokenize(text, attribute="text")
            results = crf_extractor.process(text)
            
            if results is not None:
                insert_structured_data(ml_version_id, annotation.data_source_id, results, type_coordinate, text_value.value, annotation.id)
            # insert results

def get_avg_confidence(crf_data):
    if len(crf_data) == 0: 
        return None
    total = 0.0
    for entity in crf_data:
        total+=entity["confidence"]
    return total/len(crf_data)

def insert_structured_data(ml_version_id, data_source_id, crf_data, group_coordinates, group_type, parent_annotation_id):
    print("Inserting structured data")
    grouping_annotation = insert_annotation("business grouping type", ml_version_id, data_source_id, None, "structured business grouping type", parent_annotation_id)
    grouping_coordinate = insert_coordinates(grouping_annotation.id, group_coordinates.x, group_coordinates.y, group_coordinates.width, group_coordinates.height)
    grouping_text_value = insert_text_value(grouping_coordinate.id, "business grouping type", group_type)

    avg_confidence = get_avg_confidence(crf_data)
    listing_annotation = insert_annotation("business listing", ml_version_id, data_source_id, avg_confidence, "structured business listing", parent_annotation_id)
    for entity in crf_data:
        coordinate = insert_entity_coordinates(listing_annotation.id, entity)
        text_value = insert_entity_text_value(coordinate.id, entity)


def insert_annotation(source_type, ml_version_id, data_source_id, avg_confidence, subject_type, parent_annotation_id):
    repo = Repository()
    annotation = Annotation()
    annotation.parent_id = parent_annotation_id
    annotation.source_type = source_type
    annotation.ml_version_id = ml_version_id
    annotation.data_source_id = data_source_id
    annotation.confidence = avg_confidence
    annotation.subject_type  = subject_type
    annotation.created_at = datetime.now()
    annotation.id = repo.insert_annotation(annotation)
    annotation.parent_id = parent_annotation_id
    return annotation



def insert_entity_coordinates(annotation_id, crf_entity):
    x = crf_entity["start"]
    w = crf_entity["end"] - crf_entity["start"]
    return insert_coordinates(annotation_id, x, None, w, None)

def insert_coordinates(annotation_id, x, y, w, h):
    repo = Repository()
    coord = Coordinate()
    coord.x = x
    coord.y = y
    coord.width = w
    coord.height = h
    coord.annotation_id =  annotation_id
    coord.id = repo.insert_coordinates(coord)
    return coord


def insert_entity_text_value(coordinates_id, crf_entity):
    return insert_text_value(coordinates_id, crf_entity["entity"].replace("_", " "), crf_entity["value"])

def insert_text_value(coordinates_id, key, value):
    repo = Repository()
    text_value = TextValue()
    text_value.key = key
    text_value.value = value
    text_value.coordinates_id = coordinates_id
    text_value.id = repo.insert_text_value(text_value)
    return text_value



if __name__ == "__main__":
    main()