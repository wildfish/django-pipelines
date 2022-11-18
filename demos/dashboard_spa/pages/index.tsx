import client from "../apollo_client";
import {gql} from "@apollo/client";
import {Dashboard} from "@/types";
import {DashboardGrid} from "@/components/dashboard";

export async function getServerSideProps() {
    const {data} = await client.query({
        query: gql`
        {
          dashboards {
            Meta {
              name
              slug
            }
            components {
              key
              value
              gridCssClasses
              isDeferred
              renderType
            }
          }
        }
      `,
    });

  return {
    props: {
      dashboards: data.dashboards,
    },
  }
}

type DashboardProps = {
  dashboards: Dashboard[]
};

const Home = ({dashboards}: DashboardProps) => {
    return <DashboardGrid dashboard={dashboards[0]}/>
};

export default Home
