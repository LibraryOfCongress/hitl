--
-- PostgreSQL database dump
--

-- Dumped from database version 12.5
-- Dumped by pg_dump version 13.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Annotation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Annotation" (
    id integer NOT NULL,
    source_type text,
    ml_version_id integer,
    cs_task_id integer,
    data_source_id integer,
    confidence double precision,
    subject_type_id integer,
    created_at timestamp without time zone,
    subject_type text,
    parent_id integer
);


ALTER TABLE public."Annotation" OWNER TO postgres;

--
-- Name: Annotation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Annotation_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Annotation_id_seq" OWNER TO postgres;

--
-- Name: Annotation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Annotation_id_seq" OWNED BY public."Annotation".id;


--
-- Name: CS_Task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."CS_Task" (
    id integer NOT NULL,
    name text,
    definition text,
    type text,
    input_type text,
    output_type text,
    num_votes integer,
    description text
);


ALTER TABLE public."CS_Task" OWNER TO postgres;

--
-- Name: CS_Task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."CS_Task_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."CS_Task_id_seq" OWNER TO postgres;

--
-- Name: CS_Task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."CS_Task_id_seq" OWNED BY public."CS_Task".id;


--
-- Name: Coordinates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Coordinates" (
    id integer NOT NULL,
    x double precision,
    y double precision,
    width double precision,
    height double precision,
    annotation_id integer,
    external_id text
);


ALTER TABLE public."Coordinates" OWNER TO postgres;

--
-- Name: Coordinates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Coordinates_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Coordinates_id_seq" OWNER TO postgres;

--
-- Name: Coordinates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Coordinates_id_seq" OWNED BY public."Coordinates".id;


--
-- Name: Data_Source; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Data_Source" (
    id integer NOT NULL,
    name text,
    type text,
    source_system text,
    source_id text,
    parent_id integer,
    source_url text,
    source_image_url text,
    height double precision,
    width double precision,
    location text,
    x double precision,
    y double precision,
    annotation_id integer
);


ALTER TABLE public."Data_Source" OWNER TO postgres;

--
-- Name: Data_Source_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Data_Source_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Data_Source_id_seq" OWNER TO postgres;

--
-- Name: Data_Source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Data_Source_id_seq" OWNED BY public."Data_Source".id;


--
-- Name: ML_Process; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ML_Process" (
    id integer NOT NULL,
    name text,
    description text,
    type text,
    input_type text,
    output_type text
);


ALTER TABLE public."ML_Process" OWNER TO postgres;

--
-- Name: ML_Process_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."ML_Process_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."ML_Process_id_seq" OWNER TO postgres;

--
-- Name: ML_Process_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."ML_Process_id_seq" OWNED BY public."ML_Process".id;


--
-- Name: ML_Version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ML_Version" (
    id integer NOT NULL,
    ml_process_id integer,
    train_size integer,
    validate_size integer,
    train_accuracy double precision,
    validate_accuracy double precision,
    date_time timestamp without time zone,
    version_number text
);


ALTER TABLE public."ML_Version" OWNER TO postgres;

--
-- Name: ML_Version_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."ML_Version_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."ML_Version_id_seq" OWNER TO postgres;

--
-- Name: ML_Version_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."ML_Version_id_seq" OWNED BY public."ML_Version".id;


--
-- Name: Subject_Type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Subject_Type" (
    id integer NOT NULL,
    name text,
    description text
);


ALTER TABLE public."Subject_Type" OWNER TO postgres;

--
-- Name: Subject_Type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Subject_Type_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Subject_Type_id_seq" OWNER TO postgres;

--
-- Name: Subject_Type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Subject_Type_id_seq" OWNED BY public."Subject_Type".id;


--
-- Name: Text_Value; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Text_Value" (
    id integer NOT NULL,
    key text,
    value text,
    coordinates_id integer,
    external_id text
);


ALTER TABLE public."Text_Value" OWNER TO postgres;

--
-- Name: TextValue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."TextValue_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."TextValue_id_seq" OWNER TO postgres;

--
-- Name: TextValue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."TextValue_id_seq" OWNED BY public."Text_Value".id;


--
-- Name: Train; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Train" (
    id integer NOT NULL,
    annotation_id integer,
    ml_version_id integer,
    train_type text
);


ALTER TABLE public."Train" OWNER TO postgres;

--
-- Name: Train_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Train_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Train_id_seq" OWNER TO postgres;

--
-- Name: Train_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Train_id_seq" OWNED BY public."Train".id;


--
-- Name: Training_Dataset; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Training_Dataset" (
    id integer NOT NULL,
    ml_version_id integer,
    path text
);


ALTER TABLE public."Training_Dataset" OWNER TO postgres;

--
-- Name: Training_Dataset_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Training_Dataset_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Training_Dataset_id_seq" OWNER TO postgres;

--
-- Name: Training_Dataset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Training_Dataset_id_seq" OWNED BY public."Training_Dataset".id;


--
-- Name: Annotation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Annotation" ALTER COLUMN id SET DEFAULT nextval('public."Annotation_id_seq"'::regclass);


--
-- Name: CS_Task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CS_Task" ALTER COLUMN id SET DEFAULT nextval('public."CS_Task_id_seq"'::regclass);


--
-- Name: Coordinates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinates" ALTER COLUMN id SET DEFAULT nextval('public."Coordinates_id_seq"'::regclass);


--
-- Name: Data_Source id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Data_Source" ALTER COLUMN id SET DEFAULT nextval('public."Data_Source_id_seq"'::regclass);


--
-- Name: ML_Process id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ML_Process" ALTER COLUMN id SET DEFAULT nextval('public."ML_Process_id_seq"'::regclass);


--
-- Name: ML_Version id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ML_Version" ALTER COLUMN id SET DEFAULT nextval('public."ML_Version_id_seq"'::regclass);


--
-- Name: Subject_Type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Subject_Type" ALTER COLUMN id SET DEFAULT nextval('public."Subject_Type_id_seq"'::regclass);


--
-- Name: Text_Value id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Text_Value" ALTER COLUMN id SET DEFAULT nextval('public."TextValue_id_seq"'::regclass);


--
-- Name: Train id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Train" ALTER COLUMN id SET DEFAULT nextval('public."Train_id_seq"'::regclass);


--
-- Name: Training_Dataset id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Training_Dataset" ALTER COLUMN id SET DEFAULT nextval('public."Training_Dataset_id_seq"'::regclass);


--
-- Name: Annotation Annotation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Annotation"
    ADD CONSTRAINT "Annotation_pkey" PRIMARY KEY (id);


--
-- Name: CS_Task CS_Task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CS_Task"
    ADD CONSTRAINT "CS_Task_pkey" PRIMARY KEY (id);


--
-- Name: Coordinates Coordinates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinates"
    ADD CONSTRAINT "Coordinates_pkey" PRIMARY KEY (id);


--
-- Name: Data_Source Data_Source_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Data_Source"
    ADD CONSTRAINT "Data_Source_pkey" PRIMARY KEY (id);


--
-- Name: ML_Process ML_Process_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ML_Process"
    ADD CONSTRAINT "ML_Process_pkey" PRIMARY KEY (id);


--
-- Name: ML_Version ML_Version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ML_Version"
    ADD CONSTRAINT "ML_Version_pkey" PRIMARY KEY (id);


--
-- Name: Subject_Type Subject_Type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Subject_Type"
    ADD CONSTRAINT "Subject_Type_pkey" PRIMARY KEY (id);


--
-- Name: Text_Value TextValue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Text_Value"
    ADD CONSTRAINT "TextValue_pkey" PRIMARY KEY (id);


--
-- Name: Train Train_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Train"
    ADD CONSTRAINT "Train_pkey" PRIMARY KEY (id);


--
-- Name: Training_Dataset Training_Dataset_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Training_Dataset"
    ADD CONSTRAINT "Training_Dataset_pkey" PRIMARY KEY (id);


--
-- Name: Data_Source annotation_id_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Data_Source"
    ADD CONSTRAINT annotation_id_unique UNIQUE (annotation_id);


--
-- Name: Coordinates unique_external_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinates"
    ADD CONSTRAINT unique_external_id UNIQUE (external_id);


--
-- Name: Text_Value unique_external_id_text_value; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Text_Value"
    ADD CONSTRAINT unique_external_id_text_value UNIQUE (external_id);


--
-- Name: Data_Source annofk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Data_Source"
    ADD CONSTRAINT annofk FOREIGN KEY (annotation_id) REFERENCES public."Annotation"(id) MATCH FULL;


--
-- Name: Text_Value textvaluefk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Text_Value"
    ADD CONSTRAINT textvaluefk FOREIGN KEY (coordinates_id) REFERENCES public."Coordinates"(id) MATCH FULL;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM rdsadmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

