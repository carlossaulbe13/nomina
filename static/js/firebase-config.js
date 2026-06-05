const firebaseConfig = {
  apiKey: "AIzaSyBEGU0rikK7fbICaiAnO214yWp187M9LKM",
  authDomain: "nomina-790b9.firebaseapp.com",
  databaseURL: "https://nomina-790b9-default-rtdb.firebaseio.com",
  projectId: "nomina-790b9",
  storageBucket: "nomina-790b9.firebasestorage.app",
  messagingSenderId: "53264427704",
  appId: "1:53264427704:web:a051600eb5b54bbb6d624d"
};

if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

const db = firebase.database();
const fbAuth = firebase.auth();
