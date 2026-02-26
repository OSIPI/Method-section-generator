import {
    IconBrandGithub,
    IconFileTypeDoc,
    IconSitemap,
    IconUpload,
    IconReport,
    IconExclamationCircle,
    IconAlertTriangle,
    IconTransform
} from "@tabler/icons-react"
import { TItems } from "@/types";

const NavData: {
    navMain: TItems[];
    navSecondary: TItems[];
} = {
    navMain: [
        {
            title: "Upload",
            url: "/",
            icon: IconUpload,
            showCount: false,
        },
        {
            title: "Report",
            url: "/report",
            icon: IconReport,
            showCount: false,
        },
        {
            title: "Errors",
            url: "/report/errors",
            icon: IconExclamationCircle,
            showCount: true,
            countType: "errors",
        },
        {
            title: "Warnings",
            url: "/report/warnings",
            icon: IconAlertTriangle,
            showCount: true,
            countType: "warnings",
        },
        {
            title: "Convert DICOM to BDIS",
            url: "/convert/dcm-to-bdis",
            icon: IconTransform,
            showCount: false,
        }
    ],
    navSecondary: [
        {
            title: "Documentation",
            url: "https://docs.page/osipi/Method-section-generator",
            icon: IconFileTypeDoc,
        },
        {
            title: "Github Repository",
            url: "https://github.com/OSIPI/Method-section-generator",
            icon: IconBrandGithub,
        },
        {
            title: "OSIPI TF 4.1: ASL Lexicon",
            url: "https://osipi.ismrm.org/task-forces/tf4-1/",
            icon: IconSitemap,
        },
    ],
}

export default NavData