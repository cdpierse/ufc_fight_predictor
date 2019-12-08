import React, {useState, useEffect} from 'react';
import {Button, Form, FormGroup, Label, Input } from 'reactstrap';


const SelectionGrid = () => {
    
    const url = "http://localhost:5000/fight-predictor/api/v1.0/fighters"
    const  [fighterNames, setFighterNames] =  useState([])

    async function fetchData() {
        const res = await fetch(url);
        res
          .json()
          .then(res => setFighterNames(res['fighter_names']))
      }

    useEffect(() => {
        fetchData();
      },[]);

    return (
        <Form >
            <FormGroup >
                <Label for="Fighter1" className="mr-sm-2">Fighter 1</Label>
                <Input type="select" name="select" id="f1Select" placeholder='select'>
                <option>Select a fighter </option>
                {fighterNames.map(name => (
                    <option key={name}>{name}</option>
            ))}
                </Input>

            </FormGroup>
            <FormGroup >
                <Label for="Fighter2" className="mr-sm-2">Fighter2</Label>
                <Input type="select" name="select" id="f2Select">
                <option>Select a fighter </option>
                {fighterNames.map(name => (
                    <option key={name}>{name}</option>
            ))}
                </Input>
            </FormGroup>
            <Button>Predict</Button>
        </Form>
    )
}

export default SelectionGrid