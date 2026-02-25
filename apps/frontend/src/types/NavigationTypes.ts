import {type Icon} from "@tabler/icons-react";

type TItems = {
    title: string
    url: string
    icon?: Icon
    showCount?: boolean
    countType?: "errors" | "warnings"
}

export type {
    TItems
}