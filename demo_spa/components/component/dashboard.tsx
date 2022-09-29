import React, {useContext, useMemo} from "react";
import {Component as ComponentType, Dashboard, DashboardComponentTypes, Value} from "@/types";
import {gql, useQuery} from "@apollo/client";
import {Stat} from "@/components/component/text";
import {Plotly} from "@/components/component/charts";
import {ReactTable, Tabulator} from "@/components/component/table";
import {HTML, CTA} from "@/components/component/html";
import {Form} from "@/components/component/forms";
import * as styles from "@/components/component/index.module.scss";
import {FilterContext} from "../../appContext";

/*
  We'd want something a bit more complex here/with the gql for a prod system, renderType
  is the component, but the nature of the `SomeCalculateText`/deferred ones is that they
  will often override. You can set `render_type` in be also but not much thought has gone into that yet.
 */
const DashboardComponentMap = {
    [DashboardComponentTypes.Text]: HTML,
    [DashboardComponentTypes.SomeCalculateText]: HTML,
    [DashboardComponentTypes.HTML]: HTML,
    [DashboardComponentTypes.Chart]: Plotly,
    [DashboardComponentTypes.Table]: ReactTable, //Tabulator,
    [DashboardComponentTypes.Stat]: Stat,
    [DashboardComponentTypes.Map]: Plotly,
    [DashboardComponentTypes.Form]: Form,
    [DashboardComponentTypes.CTA]: CTA,
}

type LazyComponentProps = {
    dashboard: Dashboard
    component: ComponentType
    Component: React.FC<{value: Value}>
}


const LazyComponent = ({dashboard, component, Component}: LazyComponentProps) => {
    const [filters, setFilter] = useContext(FilterContext)
    const componentFilters = useMemo(() => filters[component.key], [filters, component.key])
    const { loading, data, previousData } = useQuery(gql`
      query ($slug: String!, $key: String!, $filters: JSON) {
        component(slug: $slug, key: $key, filters: $filters) {
          value
        }
      }
    `,
        {
            variables: {
                slug:dashboard.Meta.slug,
                key: component.key,
                filters: componentFilters
            }
        }
    );

    return <>
       {loading && previousData === null || (!data && !previousData) ? <>Loading...</> : <Component componentKey={component.key} value={(data || previousData).component.value}/>}
    </>
};

type DashboardComponentProps = {
    dashboard: Dashboard
    component: ComponentType
    className?: string
}

export const DashboardComponent = ({dashboard, component}: DashboardComponentProps) => {
    const Component = DashboardComponentMap[component.renderType]
    return <div className={styles.componentInner}>
        {Object.keys(DashboardComponentMap).includes(component.renderType) ?
            !component.isDeferred ?
                <Component componentKey={component.key} value={component.value}/>
            :
                <LazyComponent dashboard={dashboard} component={component} Component={Component}/>
        :
            <div>Missing dashboard component mapping</div>
        }
    </div>
}
