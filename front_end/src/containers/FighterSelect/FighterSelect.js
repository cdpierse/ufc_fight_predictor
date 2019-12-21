import React, { useState, useEffect, useReducer } from 'react';
import { Button, Form, FormGroup, Label, Input } from 'reactstrap';
import Select from 'react-select';

const initialState = {
    fighter1: '',
    fighter2: '',
}
function reducer(state, { field, value }) {
    return {
        ...state,
        [field]: value
    }
}

const PredictionGrid = () => {

    const fighters_url = "https://fight-predictor-api.herokuapp.com/api/v1.0/fighters"
    const predict_url = "https://fight-predictor-api.herokuapp.com/api/v1.0/predict"
    const [fighterNames, setFighterNames] = useState([])
    const [selectedFighters, dispatch] = useReducer(reducer, initialState)
    const [winner, setWinner] = useState("")
    const [confidence, setConfidence] = useState("")


    const onChange = (e) => {
        console.log(e)
        dispatch({ field: e.field, value: e.value })
    }

    const makePredictionQuery = (e) => {
        const querystring = require('query-string')
        const query = querystring.stringify(e)
        return query

    }
    const onClick = (e) => {
        setConfidence("")
        setWinner("")
        if (e.fighter1 && e.fighter2) {
            console.log("Both populated")
            const query = makePredictionQuery(e)
            fetchPrediction(query)
        } else {
            console.log('Please select 2 fighters')
        }
    }

    async function fetchPrediction(query) {
        const fullQuery = predict_url.concat('?', query)
        console.log(fullQuery)
        const res = await fetch(fullQuery)
        res
            .json()
            .then(
                res => {
                    setConfidence(((Number(res['confidence']) * 100).toFixed(2)).toString() + "%")
                    setWinner(res['winner'])
                }
            )
        console.log(res)
    }



    const { fighter1, fighter2 } = selectedFighters


    async function fetchFighterData() {
        const res = await fetch(fighters_url);
        res
            .json()
            .then(res => setFighterNames(res['fighter_names'].sort()))
    }

    useEffect(() => {
        fetchFighterData();
    }, []);

    const options1 = fighterNames.map(v => ({
        label: v,
        value: v,
        field: 'fighter1'
      }));
    const options2 = fighterNames.map(v => ({
        label: v,
        value: v,
        field: 'fighter2'

      }));
    console.log(selectedFighters)
    return (
        <Form >
            <FormGroup >
                <Label for="Fighter1" className="mr-sm-2">Fighter 1</Label>
                <Select 
                name = 'fighter1'
                value= {options1.find(option => option.value === {fighter1})}
                options={options1}
                onChange = {onChange} />
                {/* <select
                    name="fighter1"
                    value={fighter1}
                    className="form-control selectpicker"
                    onChange={onChange}
                    id="f1Select"
                    placeholder='Choose Fighter 1' >
                    <option value="" disabled selected>Select Fighter 1 </option>
                    {fighterNames.map(name => (
                        <option key={name}>{name}</option>
                    ))}
                </select> */}
            </FormGroup>
            <FormGroup >
                <Label for="Fighter2" className="mr-sm-2">Fighter 2</Label>
                <Select 
                name = 'fighter2'
                value= {options2.find(option => option.value === {fighter2})}
                options={options2}
                onChange = {onChange} />
                {/* <select
                    name="fighter2"
                    value={fighter2}
                    className="form-control selectpicker"
                    onChange={onChange}
                    id="f2Select"
                    placeholder='Choose Fighter 2' >
                    <option value="" disabled selected>Select Fighter 2 </option>
                    {fighterNames.map(name => (
                        <option key={name}>{name}</option>
                    ))}
                </select> */}

            </FormGroup>
            <Button className="predictButton" onClick={() => onClick(selectedFighters)}>
                Predict
            </Button>
            <h1 className="winner">Winner:</h1>
            <h1 className="winnerResult"> {winner}</h1>
            <h1 className="confidence"> Confidence:</h1>
            <h1 className="confidenceResult"> {confidence}  </h1>
        </Form>

    )
}

export default PredictionGrid