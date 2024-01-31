const data1 = '"db2".data1';
const data2 = '"db2".data2';
const data3 = '"db2".data3';
const data4 = '"db2".data4';

function update(param,data) {
    fetch(window.location.href, {method: 'POST',body: `${param}=${data}` })
}

function send_data1() {
    update(data1,document.getElementById("data1_out").value);
}
function send_data2() {
    update(data1,document.getElementById("data2_out").value);
}
function send_data3() {
    update(data1,document.getElementById("data3_out").value);
}
function send_data4() {
    update(data1,document.getElementById("data4_out").value);
}

async function pollData() {
    const response = await fetch(window.location.href.replace("index.html","data/data.html"));
    const data = await response.json();
    if (!response.ok) {
        console.warn(`error on pollFull code:${response.status}`);
        return;
    }
    document.getElementById("data1_in").innerHTML = data.data1;
    document.getElementById("data2_in").innerHTML = data.data2;
    document.getElementById("data3_in").innerHTML = data.data3;
    document.getElementById("data4_in").innerHTML = data.data4;
}