import React from 'react'
import Plot from 'react-plotly.js'

export default class App extends React.Component {

  constructor(){
    super();

    this.state = {
      tickers: 'AAPL,HD,WMT',
      rf: 0.05,
      target_beta: 1.2,
      target_return: 1.00,
      balance: 10000,
      sock: null,
      response: null
    }

    this.changeVar = this.changeVar.bind(this)
    this.sendData = this.sendData.bind(this)
    this.generateTable = this.generateTable.bind(this)
    this.generatePlot = this.generatePlot.bind(this)
  }

  componentDidMount(){
    const socket = new WebSocket("ws://localhost:8080")
    socket.onmessage = (evt) => {
      this.setState({ response: JSON.parse(evt.data) })
    }
    this.setState({ sock: socket })
  }

  changeVar(evt){
    this.setState({ [evt.target.name]: evt.target.value })
  }

  sendData(evt){
    const { tickers, rf, target_beta, target_return, balance, sock } = this.state
    const message = {
      'tickers': tickers,
      'riskfree': rf,
      'beta': target_beta,
      'return': target_return,
      'balance': balance
    }
    sock.send(JSON.stringify(message))
    evt.preventDefault()
  }

  generatePlot(){
    const plots = []
    const { response } = this.state
    if(response !== null){
      plots.push(
        <Plot
          data={[{
            values: response['minrisk'],
            labels: response['tickers'],
            type: 'pie',
            textinfo: 'label+percent',
            insidetextorientation: 'radial'
          }]}
          layout={{
            title: 'Minimized Risk Chart',
            width: 400,
            height: 400
          }}
        />
      )
      plots.push(
        <Plot
          data={[{
            values: response['maxretn'],
            labels: response['tickers'],
            type: 'pie',
            textinfo: 'label+percent',
            insidetextorientation: 'radial'
          }]}
          layout={{
            title: 'Maximized Return Chart',
            width: 400,
            height: 400
          }}
        />
      )
    }
    return plots 
  }

  generateTable(){
    const hold = []
    const gold = []
    const { response } = this.state
    if(response !== null){
      response['table'].forEach(row => {
        const rows = []
        row.forEach(col => {
          rows.push(
            <td>{col}</td>
          )
        })
        hold.push(
          <tr>
            {rows}
          </tr>
        )
      })
      gold.push(
        <table style={{backgroundColor: 'black', color: 'orange', textAlign: 'center', width: 110}}>
          {hold}
        </table>
      )
    }
    return gold 
  }

  render(){

    return (
      <React.Fragment>
        <center>
          <div style={{backgroundColor: 'blue', color: 'cyan', textAlign: 'center', fontSize: 35}}>Portfolio Optimizer</div>
          <br/>
          <div>Enter stock tickers</div>
          <input name="tickers" value={this.state.tickers} onChange={this.changeVar} style={{backgroundColor: 'red', color: 'white', textAlign: 'center', fontSize: 20, width: 400}}></input>
          <br/>
          <table style={{textAlign: 'center'}}>
            <tr>
              <td>RiskFreeRate</td>
              <td>TargetBeta</td>
              <td>TargetReturn</td>
              <td>Balance</td>
            </tr>
            <tr>
              <td><input name="rf" value={this.state.rf} onChange={this.changeVar} style={{backgroundColor: 'green', color: 'white', textAlign: 'center', fontSize: 12, width: 100}}></input></td>
              <td><input name="target_beta" value={this.state.target_beta} onChange={this.changeVar} style={{backgroundColor: 'green', color: 'white', textAlign: 'center', fontSize: 12, width: 100}}></input></td>
              <td><input name="target_return" value={this.state.target_return} onChange={this.changeVar} style={{backgroundColor: 'green', color: 'white', textAlign: 'center', fontSize: 12, width: 100}}></input></td>
              <td><input name="balance" value={this.state.balance} onChange={this.changeVar} style={{backgroundColor: 'green', color: 'white', textAlign: 'center', fontSize: 12, width: 100}}></input></td>
            </tr>
          </table>
          <br/>
          <br/>
          <button style={{backgroundColor: 'yellow', color: 'gray', width: 90}} onClick={this.sendData}>Get Data</button>
          <br/>
          <br/>
          <div>{this.generateTable()}</div>
          <br/>
          <div>{this.generatePlot()}</div>
        </center>
      </React.Fragment>
    );
  }

}