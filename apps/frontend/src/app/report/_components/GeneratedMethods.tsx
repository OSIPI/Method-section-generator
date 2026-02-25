"use client";

import {useState, useRef, useEffect} from "react";
import {Textarea} from "@/components/ui/textarea";
import {Card} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {ClipboardCopy, Download} from "lucide-react";
import { toast } from "sonner"

export default function GeneratedMethods({text: initialText, type}: { text: string, type: string }) {
    const [text, setText] = useState(initialText);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [isEditing, setIsEditing] = useState(false);
    
    useEffect(() => {
        setText(initialText);
        if (initialText !== "") {
            setIsEditing(true);
        } else {
            setIsEditing(false);
        }
    }, [initialText]);

    const handleCopy = () => {
        if (textareaRef.current) {
            navigator.clipboard.writeText(textareaRef.current.value)
                .then(() => {
                    console.log("Text copied to clipboard");
                })
                .catch(err => {
                    console.error("Failed to copy text: ", err);
                });

            toast.success("Methods copied to clipboard!");
        }
    };

    const handleDownload = () => {
        if (text) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report.${type}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            toast.success("Methods downloaded successfully!");
        } else {
            toast.error("No content to download");
        }
    };

    return (
        <Card className="h-full py-0 p-2 bg-gray-50 dark:bg-secondary relative">

            <div className="absolute top-2 right-2 z-10 flex gap-0.5">
                <Button
                    onClick={handleDownload}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-gray-200 dark:hover:bg-gray-700"
                    aria-label="Download report"
                >
                    <Download className="h-4 w-4"/>
                </Button>
                <Button
                    onClick={handleCopy}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-gray-200 dark:hover:bg-gray-700"
                    aria-label="Copy to clipboard"
                >
                    <ClipboardCopy className="h-4 w-4"/>
                </Button>
            </div>

            <Textarea
                ref={textareaRef}
                className="w-full md:text-lg h-full border-none shadow-none bg-transparent dark:text-gray-200 dark:placeholder-gray-400 text-lg"
                placeholder="Generated methods will appear here..."
                readOnly={!isEditing}
                value={text}
                onChange={(e) => setText(e.target.value)}
            />
        </Card>
    );
}