#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to parse Mexico GeoJSON data and extract hierarchical administrative divisions
(states and municipalities) into SQL statements for database insertion.
"""

import os
import json
import codecs
from collections import defaultdict

def load_geojson(file_path):
    """Load GeoJSON file and return the data."""
    try:
        with codecs.open(file_path, 'r', 'utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_admin_divisions(geojson_data):
    """Extract administrative divisions from GeoJSON data."""
    if not geojson_data or 'features' not in geojson_data:
        return []

    admin_divisions = []

    for feature in geojson_data['features']:
        if 'properties' in feature:
            props = feature['properties']

            # Extract relevant fields
            admin_division = {
                'cvegeo': props.get('CVEGEO', ''),
                'cve_ent': props.get('CVE_ENT', ''),
                'cve_mun': props.get('CVE_MUN', ''),
                'nomgeo': props.get('NOMGEO', ''),
                'nom_ent': props.get('NOM_ENT', '')
            }

            admin_divisions.append(admin_division)

    return admin_divisions

def generate_create_tables_sql():
    """Generate SQL statements to create the tables for hierarchical structure."""
    sql = """
-- 州表
CREATE TABLE mexico_states (
    id INTEGER PRIMARY KEY,                -- 主键ID
    cve_ent VARCHAR(2),                    -- 州编码
    nom_ent VARCHAR(100)                   -- 州名称
);

-- 市/县表
CREATE TABLE mexico_municipalities (
    id INTEGER PRIMARY KEY,                -- 主键ID
    cvegeo VARCHAR(10),                    -- 地理编码（唯一标识符）
    cve_ent VARCHAR(2),                    -- 州编码
    cve_mun VARCHAR(3),                    -- 市/县编码
    nomgeo VARCHAR(100),                   -- 市/县名称
    state_id INTEGER,                      -- 关联州表的外键
    FOREIGN KEY (state_id) REFERENCES mexico_states(id)
);
"""
    return sql

def generate_insert_sql_hierarchical(states, municipalities):
    """Generate SQL INSERT statements for the hierarchical structure."""
    sql_statements = []

    # Insert states
    for i, (cve_ent, nom_ent) in enumerate(states.items(), 1):
        sql = f"""INSERT INTO mexico_states (id, cve_ent, nom_ent)
VALUES ({i}, '{cve_ent}', '{nom_ent.replace("'", "''")}');"""
        sql_statements.append(sql)

    # Insert municipalities with reference to state
    for i, municipality in enumerate(municipalities, 1):
        # Find state id
        state_id = 0
        for j, (cve_ent, _) in enumerate(states.items(), 1):
            if cve_ent == municipality['cve_ent']:
                state_id = j
                break

        sql = f"""INSERT INTO mexico_municipalities (id, cvegeo, cve_ent, cve_mun, nomgeo, state_id)
VALUES ({i}, '{municipality['cvegeo']}', '{municipality['cve_ent']}', '{municipality['cve_mun']}', '{municipality['nomgeo'].replace("'", "''")}', {state_id});"""
        sql_statements.append(sql)

    return sql_statements

def process_state_files(states_dir):
    """Process all state files in the given directory."""
    all_admin_divisions = []
    states = {}  # Dictionary to store unique states

    # Get all JSON files in the states directory
    state_files = [f for f in os.listdir(states_dir) if f.endswith('.json')]

    for state_file in state_files:
        file_path = os.path.join(states_dir, state_file)
        geojson_data = load_geojson(file_path)

        if geojson_data:
            admin_divisions = extract_admin_divisions(geojson_data)
            all_admin_divisions.extend(admin_divisions)

            # Extract state information
            for division in admin_divisions:
                cve_ent = division['cve_ent']
                nom_ent = division['nom_ent']
                if cve_ent and nom_ent:
                    states[cve_ent] = nom_ent

            print(f"Processed {state_file}: {len(admin_divisions)} municipalities found")

    return all_admin_divisions, states

def main():
    # Define the path to the states directory for the year 2023
    states_dir = os.path.join('2023', 'states')

    # Process all state files
    admin_divisions, states = process_state_files(states_dir)

    if not admin_divisions:
        print("No administrative divisions found.")
        return

    print(f"Total administrative divisions found: {len(admin_divisions)}")
    print(f"Total states found: {len(states)}")

    # Generate SQL statements for hierarchical structure
    create_tables_sql = generate_create_tables_sql()
    insert_statements = generate_insert_sql_hierarchical(states, admin_divisions)

    # Write SQL to file
    output_file = 'mexico_admin_divisions_hierarchical.sql'
    with codecs.open(output_file, 'w', 'utf-8') as f:
        f.write(create_tables_sql)
        f.write('\n')
        for statement in insert_statements:
            f.write(statement)
            f.write('\n')

    print(f"SQL statements written to {output_file}")

if __name__ == "__main__":
    main()
