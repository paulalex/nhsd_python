"""
How many successful deployments have taken place?

How does this break down by project group, by environment, by year?

Which is the most popular day of the week for live deployments?

What is the average length of time a release takes from integration to live, by project group?

Please provide a break down by project group of success and unsuccessful deployments
(successful being releases that are deployed to live), the number of deployments involved in
the release pipeline and whether some environments had to be repeatedly deployed.
"""
import json
from datetime import datetime


def load_data():
    with open("projects.json", "r") as read_file:
        data = json.load(read_file)["projects"]

        return data


def get_full_break_down(data):
    group_breakdown = {}
    releases_by_group = get_releases_by_group(data)

    for group in releases_by_group.keys():
        releases = releases_by_group[group]
        total_deployments = 0
        successful_deployment_count = 0
        unsuccessful_deployment_count = 0
        failure_count_by_env = {}

        for release in releases:
            for deployment in release["deployments"]:
                total_deployments = (total_deployments + 1)
                env = deployment.get('environment')
                state = deployment.get('state')

                if state == "Failed":
                    unsuccessful_deployment_count = (unsuccessful_deployment_count + 1)
                    if env not in failure_count_by_env:
                        failure_count_by_env[env] = 1
                    else:
                        failure_count_by_env[env] = (failure_count_by_env[env] + 1)
                elif state == "Success" and env == "Live":
                    successful_deployment_count = (successful_deployment_count + 1)

        repeated_deployments = sum(1 for i in failure_count_by_env.values() if i >= 2)

        repeated_deployments = "Yes" if repeated_deployments > 1 else "No"

        group_breakdown[group] = (total_deployments, successful_deployment_count, unsuccessful_deployment_count,
                                  repeated_deployments)

    return group_breakdown


def get_releases_by_group(data):
    group_dict = {}

    # Loop over each project and get releases
    for project in data:
        group = project.get("project_group")
        releases = project["releases"]

        # Process each release for a project and add to group
        for release in releases:
            if group in group_dict:
                group_dict[group].append(release)
            else:
                group_dict[group] = [release]

    return group_dict


def get_average_deployment_time_by_project_group(data):
    releases_by_group = get_days_by_project_group(data)
    avg_by_group = {}

    for group in releases_by_group.keys():
        sum_for_group = 0
        releases_by_project = releases_by_group[group]

        for release_days in releases_by_project:
            sum = 0
            for days_to_release in release_days:
                sum += days_to_release
                project_avg = round(sum / len(releases_by_project))
                sum_for_group += project_avg

        overall_avg = round(sum_for_group / len(releases_by_group))
        avg_by_group[group] = overall_avg

    return avg_by_group


def get_days_by_project_group(data):
    group_dict = {}

    # Loop over each project
    for project in data:
        group = project.get("project_group")
        releases = project["releases"]
        release_days_for_project = []

        # Process each release for a project
        for release in releases:
            # Get the days between releases as an array
            release_days = get_days_between_release(release)

            if release_days is not None and release_days > 0:
                release_days_for_project.append(release_days)

        if group in group_dict:
            group_dict[group].append(release_days_for_project)
        else:
            group_dict[group] = []
            group_dict[group].append(release_days_for_project)

    return group_dict


def get_days_between_release(release):
    deployments = release["deployments"]
    counter = len(deployments)
    end = None
    days = None
    start = None

    for i in range(counter):
        deployment = deployments[i]

        if deployment.get("environment") == "Integration" and start is None:
            start = deployment.get("created")
        elif deployment.get("state") == "Success" and deployment.get("environment") == "Live":
            end = deployment.get("created")

    if start is not None and end is not None:
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
        delta = (end - start)
        days = delta.days

    return days


def append_output_to_log(line):
    report = open("project_report.log", "a")
    report.write(line)
    report.close()


def get_number_of_successful_deployments(data):
    count = 0
    for project in data:
        releases = project["releases"]
        for release in releases:
            deployments = release["deployments"]
            for deployment in deployments:
                if deployment.get("state") == "Success":
                    count += 1

    return count


def get_breakdown_by_group(data):
    group_dict = {}

    for project in data:
        releases = project["releases"]
        group = project.get("project_group")

        for release in releases:
            deployments = release["deployments"]
            for deployment in deployments:
                if deployment.get("state") == "Success":
                    if group in group_dict:
                        group_dict[group] += 1
                    else:
                        group_dict[group] = 1
    return group_dict


def get_breakdown_by_environment(data):
    env_dict = {}

    for project in data:
        releases = project["releases"]
        for release in releases:
            deployments = release["deployments"]
            for deployment in deployments:
                env = deployment.get("environment")
                if deployment.get("state") == "Success":
                    if env in env_dict:
                        env_dict[env] = env_dict[env] + 1
                    else:
                        env_dict[env] = 1
    return env_dict


def get_breakdown_by_year(data):
    year_dict = {}

    for project in data:
        releases = project["releases"]
        for release in releases:
            deployments = release["deployments"]
            for deployment in deployments:
                created = deployment.get("created")
                created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ')
                created = created.year
                if deployment.get("state") == "Success":
                    if created in year_dict:
                        year_dict[created] = year_dict[created] + 1
                    else:
                        year_dict[created] = 1

    return year_dict


def get_count_by_day_of_week(data):
    day_dict = {}

    for project in data:
        releases = project["releases"]
        for release in releases:
            deployments = release["deployments"]
            for deployment in deployments:
                created = deployment.get("created")
                created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ')
                created = created.strftime('%A')
                if deployment.get("environment") == "Live":
                    if created in day_dict:
                        day_dict[created] = day_dict[created] + 1
                    else:
                        day_dict[created] = 1
    print(day_dict)

    day_dict_sorted = sorted(day_dict, key=(lambda key: day_dict[key]), reverse=True)

    return day_dict_sorted[0]


def report_success(data, section_header):
    total = 0

    append_output_to_log(section_header)

    for item in data:
        total += data.get(item)
        append_output_to_log(f"{item}: {data.get(item)}\n")

    append_output_to_log(f"Total: {total}\n\n")


def report_success_by_environment(data):
    append_output_to_log(f"By environment: {get_breakdown_by_environment(data)}\n")


def report_full_breakdown(breakdown_data):
    append_output_to_log("Full breakdown by group\n\n")

    for group in breakdown_data:
        data_items = breakdown_data[group]
        append_output_to_log(f"---------- {group} ---------- \n\n")
        append_output_to_log(f"Total Deployments: {data_items[0]}\n")
        append_output_to_log(f"Successful Deployments: {data_items[1]}\n")
        append_output_to_log(f"Unsuccessful Deployments: {data_items[2]}\n")
        append_output_to_log(f"Multiple Deployments Needed: {data_items[3]}\n\n")


def generate_report(data):
    append_output_to_log(f"Answer to question 1: {get_number_of_successful_deployments(data)}\n\n")

    append_output_to_log(f"Answers to question 2:\n\n")
    report_success(get_breakdown_by_group(data), "By Group:\n\n")
    report_success(get_breakdown_by_environment(data), "By Environment:\n\n")
    report_success(get_breakdown_by_year(data), "By Year:\n\n")

    append_output_to_log(f"Answer to question 3: {get_count_by_day_of_week(data)}\n\n")

    append_output_to_log(f"Answer to question 4:\n\n")
    report_success(get_average_deployment_time_by_project_group(data), "Average length of time a release takes from "
                                                                       "integration to live, by project group:\n\n")
    append_output_to_log(f"Answer to question 5:\n\n")
    report_full_breakdown(get_full_break_down(data))


def main():
    start_time = datetime.now()
    print("[INFO] Preparing report")

    data = load_data()

    end_time = datetime.now()

    generate_report(data)

    print(f'[INFO] Run time: {end_time - start_time}')


if __name__ == "__main__":
    main()
