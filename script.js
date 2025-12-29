const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const statusBox = document.getElementById("status");
const tableBody = document.getElementById("tableBody");
const cameraBox = document.getElementById("cameraBox");

let stream = null;
let verifiedCode = "";

function verifyCode() {
  const code = document.getElementById("code").value.trim();
  if (!code) {
    alert("Vui lòng nhập mã");
    return;
  }

  verifiedCode = code;
  cameraBox.classList.remove("hidden");

  navigator.mediaDevices.getUserMedia({ video: true }).then((s) => {
    stream = s;
    video.srcObject = stream;
  });

  statusBox.innerText = "Đã xác nhận mã, sẵn sàng điểm danh";
}

function startAttendance() {
  if (!verifiedCode) {
    alert("Chưa nhập mã");
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);

  const imageData = canvas.toDataURL("image/jpeg");

  fetch("http://127.0.0.1:5000/attendance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      code: verifiedCode,
      image: imageData,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (data.status === "success") {
        statusBox.className = "status success";
        statusBox.innerText = "ĐIỂM DANH THÀNH CÔNG (" + data.accuracy + "%)";
        loadToday();
      } else {
        statusBox.className = "status fail";
        statusBox.innerText = "ĐIỂM DANH KHÔNG THÀNH CÔNG";
      }
    });
}

function loadToday() {
  fetch("http://127.0.0.1:5000/today")
    .then((res) => res.json())
    .then((data) => {
      tableBody.innerHTML = "";
      if (data.length === 0) {
        tableBody.innerHTML =
          "<tr><td colspan='5'>Chưa có ai điểm danh</td></tr>";
        return;
      }

      data.forEach((row) => {
        tableBody.innerHTML += `
          <tr>
            <td>${row.code}</td>
            <td>${row.name}</td>
            <td>${row.class}</td>
            <td>${row.date}</td>
            <td>${row.time}</td>
          </tr>
        `;
      });
    });
}
function searchStudent() {
  const code = document.getElementById("searchCode").value.trim();
  const box = document.getElementById("searchResult");

  if (!code) {
    box.innerHTML = "❌ Vui lòng nhập mã";
    return;
  }

  fetch("http://127.0.0.1:5000/search/" + code)
    .then((res) => res.json())
    .then((data) => {
      if (data.status !== "success") {
        box.innerHTML = "❌ Không tìm thấy mã này";
        return;
      }

      box.innerHTML = `
        <div><b>Mã:</b> ${data.code}</div>
        <div><b>Tên:</b> ${data.name}</div>
        <div><b>Lớp:</b> ${data.class}</div>
        <img src="http://127.0.0.1:5000/storage/${data.image}">
      `;
    });
}
