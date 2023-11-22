import React, {useCallback, useEffect, useState} from 'react';
import axios from 'axios'
// const ReactTable = window.ReactTable.default

function Invoice() {

    const [file, setFile] = useState()
    const [descriptiondata, setDescriptiondata] = useState([])
    const [otherdata, setOtherdata] = useState([])
    const [description_detail_header,setDescription_detail_header] = useState([])
    const [other_detail_header,setOther_detail_header] = useState([])
    const [status_message,setMessage] = useState()

    function handleChange(event) {
        setDescriptiondata([])
        setOtherdata([])
        setDescription_detail_header([])
        setOther_detail_header([])
        setMessage()
        setFile(event.target.files[0])
    }

    function handleSubmit(event) {
        event.preventDefault()
        // const url = 'localhost:5000/v1/ocr';
        const url = 'http://185.207.251.45:7005/v1/ocr';
        const formData = new FormData();
        formData.append('file', file);
        formData.append('fileName', file.name);
        const config = {
          headers: {
            'content-type': 'multipart/pdf',
            'Access-Control-Allow-Origin': '*'
          },
        };
        axios.post(url, formData, config).then((response) => {
            setDescriptiondata(response.data.description_data)
            setOtherdata(response.data.other_data)
            setDescription_detail_header(response.data.description_detail_header)
            setOther_detail_header(response.data.other_detail_header)
            setMessage(response.data.message)
        });
      }
    
    console.log('*****************');
    console.log(descriptiondata);
    console.log(otherdata);
    console.log(description_detail_header);
    console.log(other_detail_header);
    console.log(status_message);
    console.log('*****************');

    return ( 
        <div className="App">
            <form onSubmit={handleSubmit}>
            <div id='header'>
              <h1>Invoice Upload</h1>
            </div>
            <div>
              <span>{status_message}</span>
            </div>
            <div id = 'choose_file_btn'>
              <input type="file" onChange={handleChange}/>
            </div>
            <div id = 'upload_file_btn'>
              <button type="submit">Upload</button>
            </div>
            </form>
            <div id = 'description_table'>
              <table>
                  <tr>
                    {
                      description_detail_header != null ? description_detail_header.map(header => (
                      <th>{header}</th>
                      ))
                    :''}
                  </tr>
                  {
                    descriptiondata != null ? descriptiondata.map(description => (
                    <tr>
                    <td>{description[0]}</td>
                    <td>{description[1]}</td>
                    <td>{description[2]}</td>
                    <td>{description[3]}</td>
                    <td>{description[4]}</td>
                    <td>{description[5]}</td>
                    <td>{description[6]}</td>
                    <td>{description[7]}</td>
                    <td>{description[8]}</td>
                    <td>{description[9]}</td>
                    <td>{description[10]}</td>
                    </tr>
                    )):''
                  }
                  
              </table>
            </div>
            <div id = 'other_table'>
              <table>
                  <tr>
                    {
                      other_detail_header != null ? other_detail_header.map(header => (
                      <th>{header}</th>
                      ))
                    :''}
                  </tr>
                  {
                    otherdata != null ? otherdata.map(other => (
                    <tr>
                    <td>{other[0]}</td>
                    <td>{other[1]}</td>
                    <td>{other[2]}</td>
                    <td>{other[3]}</td>
                    <td>{other[4]}</td>
                    <td>{other[5]}</td>
                    <td>{other[6]}</td>
                    <td>{other[7]}</td>
                    <td>{other[8]}</td>
                    <td>{other[9]}</td>
                    <td>{other[10]}</td>
                    </tr>
                    )):''
                  }
                  
              </table>
            </div>
        </div>
    )
}

export default Invoice;