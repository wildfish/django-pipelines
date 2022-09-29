import {LayoutComponentsWrapper} from "@/components";
import React from "react";
import {Dashboard} from "@/types";
import * as styles from "@/components/dashboard/index.module.scss";

export const DashboardWithLayout = ({dashboard}: {dashboard: Dashboard}) => {
    return <div>
        <h1>{dashboard.Meta.name} (Layout applied)</h1>
        <div className={styles.dashboardContainer}>
            <LayoutComponentsWrapper dashboard={dashboard} layoutComponents={dashboard.Meta.layoutJson.layout_components}/>
        </div>
    </div>
}