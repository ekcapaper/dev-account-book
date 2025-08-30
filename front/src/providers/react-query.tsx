import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import type {ReactNode} from "react";
// (선택) Devtools
// import { ReactQueryDevtools } from "@tanstack/react-query-devtools";


export default function ReactQueryProvider({children}: { children: ReactNode }) {
    const client = new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 60_000,
                gcTime: 5 * 60_000,
                retry: 1,
                refetchOnWindowFocus: false,
            },
            mutations: {retry: 0},
        },
    });


    return (
        <QueryClientProvider client={client}>
            {children}
            {/* <ReactQueryDevtools initialIsOpen={false} /> */}
        </QueryClientProvider>
    );
}