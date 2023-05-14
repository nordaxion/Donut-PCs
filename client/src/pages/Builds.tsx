import { useEffect, useState } from "react";
import apiClient from "src/services/apiClient";
import "../scss/builds.scss";
import Button from "src/components/Button";
import { Link } from "react-router-dom";
import pc_img from "../assets/images/pc.png";
import BuildCard from "src/components/BuildCard";

function Builds() {
  const [builds, setBuilds] = useState<any[]>([]);

  useEffect(() => {
    fetchBuilds();
  }, []);


  async function fetchBuilds() {
    const res = await apiClient.getAllBuilds();
    setBuilds(res);
  }

  return (
    <main className="builds">
      <div className="builds__banner">
        <div className="builds__banner-container">
          <div className="builds__title">
            <p style={{ color: "#54aeef" }}>{"<"}</p>
            <p>Featured Builds</p>
            <p style={{ color: "#54aeef" }}>{">"}</p>
          </div>
          <div className="builds__banner-desc">
            <p>Shop from a selection of Donut PC's many featured builds.</p>
            <p>Browse curated builds from our Employees and users like you.</p>
            <p>
              Our builds not to your specifications? Create your own unique PC.
            </p>
            <p>
              Build your own PC from start to finish using our custom PC
              builder.
            </p>
          </div>
          <Link to="/mybuild" className="builds__mybuild-btn">
            <Button
              className="black-primary"
              style={{ padding: "1rem", width: "10rem" }}
            >
              Build Your Own
            </Button>
          </Link>
        </div>
        <img className="builds__banner-img" src={pc_img} />
      </div>
      {builds.length ? (
        <div className="builds__cards">
          {builds.map((build, i) => {
            return <BuildCard build={build} key={i} />;
          })}
        </div>
      ) : (
        <div></div>
      )}
    </main>
  );
}

export default Builds;
