import PdfUploader from '../pdf_uploader/pdf_uploader';
import './home.css';

const Home = () => {
  return (
    <div className="home">
      <h1>Welcome to PDF Uploader</h1>
      <PdfUploader />
    </div>
  );
};

export default Home;